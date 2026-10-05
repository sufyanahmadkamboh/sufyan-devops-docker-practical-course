// A small HTTP API written in TypeScript: GET / and GET /health
import * as http from "node:http";
import * as os from "node:os";

const port: number = Number(process.env.PORT ?? 3000);

const server = http.createServer((req: http.IncomingMessage, res: http.ServerResponse) => {
  res.writeHead(200, { "Content-Type": "application/json" });
  if (req.url === "/health") {
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }
  res.end(JSON.stringify({ message: "Hello from TypeScript", hostname: os.hostname() }));
});

server.listen(port, "0.0.0.0", () => console.log(`ts-api listening on port ${port}`));
process.on("SIGTERM", () => server.close(() => process.exit(0)));
