// Starts the API on its own port and checks both endpoints: node --test
const { test, before, after } = require("node:test");
const assert = require("node:assert");
const { spawn } = require("node:child_process");
const path = require("node:path");

const port = 3999;
const url = (p) => `http://127.0.0.1:${port}${p}`;
let server;

before(async () => {
  server = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], {
    env: { ...process.env, PORT: String(port) },
  });
  for (let i = 0; i < 50; i++) {
    try {
      await fetch(url("/health"));
      return;
    } catch {
      await new Promise((r) => setTimeout(r, 100));
    }
  }
  throw new Error("the server did not start");
});

after(() => server.kill());

test("GET /health answers ok", async () => {
  const res = await fetch(url("/health"));
  assert.strictEqual(res.status, 200);
  assert.deepStrictEqual(await res.json(), { status: "ok" });
});

test("GET / greets", async () => {
  const body = await (await fetch(url("/"))).json();
  assert.strictEqual(body.message, "Hello from Node.js");
});
