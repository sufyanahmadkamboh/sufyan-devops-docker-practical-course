// The frontend "build": copy src/ to dist/, give app.js a content-hashed name (so browsers can cache it forever)
// and stamp the version into the page. Real projects use a bundler; the Docker side is the same.
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync, copyFileSync } from "node:fs";

const version = process.env.APP_VERSION ?? "dev";
const js = readFileSync("src/app.js");
const jsName = `app.${createHash("sha256").update(js).digest("hex").slice(0, 10)}.js`;

mkdirSync("dist", { recursive: true });
writeFileSync(`dist/${jsName}`, js);
copyFileSync("src/styles.css", "dist/styles.css");
writeFileSync("dist/index.html", readFileSync("src/index.html", "utf8")
  .replace("__APP_JS__", jsName)
  .replace("__APP_VERSION__", version));
console.log(`built dist/ (${jsName}, version ${version})`);
