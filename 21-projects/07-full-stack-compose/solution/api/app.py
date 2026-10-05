"""Notes API: GET /api/notes, POST /api/notes {"text": "..."}, GET /api/health (checks the database too)."""
import os
import time

import psycopg
from flask import Flask, jsonify, request

DSN = (f"host={os.environ.get('DB_HOST', 'db')} dbname={os.environ['DB_NAME']} "
       f"user={os.environ['DB_USER']} password={os.environ['DB_PASSWORD']} connect_timeout=3")

app = Flask(__name__)


def connect():
    return psycopg.connect(DSN)


def migrate():
    """Create the table once; Gunicorn runs this in its master process (--preload) before starting the workers."""
    for attempt in range(1, 16):
        try:
            with connect() as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, text TEXT NOT NULL)")
            return
        except psycopg.OperationalError as err:
            print(f"waiting for the database (attempt {attempt}): {err}".strip(), flush=True)
            time.sleep(2)
    raise SystemExit("database not reachable")


@app.get("/api/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return jsonify(status="ok")
    except psycopg.Error as err:
        app.logger.error("health: %s", err)
        return jsonify(status="database unavailable"), 503


@app.get("/api/notes")
def list_notes():
    with connect() as conn:
        rows = conn.execute("SELECT id, text FROM notes ORDER BY id").fetchall()
    return jsonify([{"id": i, "text": t} for i, t in rows])


@app.post("/api/notes")
def add_note():
    text = (request.get_json(silent=True) or {}).get("text", "").strip()
    if not 0 < len(text) <= 200:
        return jsonify(error='send {"text": "1-200 characters"}'), 400
    with connect() as conn:
        note_id = conn.execute("INSERT INTO notes (text) VALUES (%s) RETURNING id", (text,)).fetchone()[0]
    return jsonify(id=note_id, text=text), 201


migrate()
