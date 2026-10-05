// The capstone API: a small orders service in front of PostgreSQL.
//
//	GET  /api/health    200 when the API and the database answer, 503 otherwise
//	GET  /api/orders    the 20 latest orders
//	POST /api/orders    {"item": "flat white"} creates an order
//
// Configuration comes from the environment (PORT, APP_VERSION, PGHOST, PGPORT, PGUSER, PGDATABASE) and the database
// password from a file (PGPASSWORD_FILE, a Docker secret), never from an environment variable.
// "api -healthcheck" calls /api/health and exits 0 or 1: the image has no shell or curl for a HEALTHCHECK to use.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type order struct {
	ID      int64     `json:"id"`
	Item    string    `json:"item"`
	Created time.Time `json:"created"`
}

func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func databaseURL() (string, error) {
	password := os.Getenv("PGPASSWORD")
	if file := os.Getenv("PGPASSWORD_FILE"); file != "" {
		b, err := os.ReadFile(file)
		if err != nil {
			return "", fmt.Errorf("reading the database password: %w", err)
		}
		password = strings.TrimSpace(string(b))
	}
	u := url.URL{
		Scheme:   "postgres",
		User:     url.UserPassword(env("PGUSER", "orders"), password),
		Host:     env("PGHOST", "db") + ":" + env("PGPORT", "5432"),
		Path:     env("PGDATABASE", "orders"),
		RawQuery: "sslmode=disable",
	}
	return u.String(), nil
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func healthcheck(port string) int {
	client := http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get("http://127.0.0.1:" + port + "/api/health")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		fmt.Fprintln(os.Stderr, "health:", resp.Status)
		return 1
	}
	return 0
}

func main() {
	port := env("PORT", "8080")
	if len(os.Args) > 1 && os.Args[1] == "-healthcheck" {
		os.Exit(healthcheck(port))
	}
	log := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	version := env("APP_VERSION", "dev")

	dsn, err := databaseURL()
	if err != nil {
		log.Error("configuration", "error", err)
		os.Exit(1)
	}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		log.Error("database configuration", "error", err)
		os.Exit(1)
	}
	defer pool.Close()

	// the schema is tiny: create it when the API starts (a real service would run versioned migrations)
	migrate := func() error {
		_, err := pool.Exec(ctx, `CREATE TABLE IF NOT EXISTS orders (
			id      BIGSERIAL PRIMARY KEY,
			item    TEXT NOT NULL CHECK (length(item) BETWEEN 1 AND 100),
			created TIMESTAMPTZ NOT NULL DEFAULT now())`)
		return err
	}
	for attempt := 1; ; attempt++ {
		if err = migrate(); err == nil {
			break
		}
		if attempt == 10 {
			log.Error("database not reachable", "error", err)
			os.Exit(1)
		}
		log.Warn("waiting for the database", "attempt", attempt, "error", err)
		time.Sleep(2 * time.Second)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/health", func(w http.ResponseWriter, r *http.Request) {
		c, cancel := context.WithTimeout(r.Context(), 2*time.Second)
		defer cancel()
		if err := pool.Ping(c); err != nil {
			writeJSON(w, http.StatusServiceUnavailable, map[string]string{"status": "database unavailable"})
			return
		}
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok", "version": version})
	})
	mux.HandleFunc("GET /api/orders", func(w http.ResponseWriter, r *http.Request) {
		rows, err := pool.Query(r.Context(), "SELECT id, item, created FROM orders ORDER BY id DESC LIMIT 20")
		if err != nil {
			log.Error("list orders", "error", err)
			writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "database error"})
			return
		}
		defer rows.Close()
		orders := []order{}
		for rows.Next() {
			var o order
			if err := rows.Scan(&o.ID, &o.Item, &o.Created); err != nil {
				writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "database error"})
				return
			}
			orders = append(orders, o)
		}
		writeJSON(w, http.StatusOK, orders)
	})
	mux.HandleFunc("POST /api/orders", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			Item string `json:"item"`
		}
		if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1024)).Decode(&in); err != nil ||
			len(strings.TrimSpace(in.Item)) == 0 || len(in.Item) > 100 {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": `send {"item": "1-100 characters"}`})
			return
		}
		var o order
		err := pool.QueryRow(r.Context(), "INSERT INTO orders (item) VALUES ($1) RETURNING id, item, created",
			strings.TrimSpace(in.Item)).Scan(&o.ID, &o.Item, &o.Created)
		if err != nil {
			log.Error("create order", "error", err)
			writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "database error"})
			return
		}
		log.Info("order created", "id", o.ID)
		writeJSON(w, http.StatusCreated, o)
	})

	srv := &http.Server{Addr: ":" + port, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	go func() {
		<-ctx.Done()
		shutdown, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		_ = srv.Shutdown(shutdown)
	}()
	log.Info("listening", "port", port, "version", version)
	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Error("server", "error", err)
		os.Exit(1)
	}
	log.Info("stopped")
}
