// A small HTTP API with no dependencies: GET / and GET /health
const http = require("node:http");
const os = require("node:os");

const port = Number(process.env.PORT || 3000);
const greeting = process.env.GREETING || "Hello from Node.js";

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ status: "ok" }));
  }
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ message: greeting, hostname: os.hostname(), version: process.env.APP_VERSION || "dev" }));
});

server.listen(port, "0.0.0.0", () => console.log(`node-api listening on port ${port}`));
process.on("SIGTERM", () => server.close(() => process.exit(0)));
