<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 105 · Build cache optimization · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Apply the technique to the Node.js API in `~/docker-practice/lesson-105-node`: write a Dockerfile that installs
dependencies with `npm ci` from `package.json` and `package-lock.json` alone, then copies the code, and prove that
changing `server.js` leaves the `npm ci` step cached.

## Solution

```bash
cd ~/docker-practice/lesson-105-node
cp ~/docker-practice/lesson-105/build-steps.sh .
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
COPY . .
USER node
CMD ["node", "server.js"]
EOF
sh build-steps.sh -t cafe-node:cache . > /dev/null
echo "// change" >> server.js
sh build-steps.sh -t cafe-node:cache .
```

```text
base   [1/5] FROM docker.io/library/node:24-alpine@sha256:ebfe2f90462722a7a4d
cached [2/5] WORKDIR /app
cached [3/5] COPY package.json package-lock.json ./
cached [4/5] RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
ran    [5/5] COPY . .
```

`npm ci` (step 4) is cached; only `COPY . .` ran. The `/root/.npm` cache mount keeps npm's downloads for the times
`package-lock.json` does change.
