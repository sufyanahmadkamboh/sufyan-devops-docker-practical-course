<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 105 · Build cache optimization · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Apply the technique to the Node.js API in `~/docker-practice/lesson-105-node`: write a Dockerfile that installs
dependencies with `npm ci` from `package.json` and `package-lock.json` alone, then copies the code, and prove that
changing `server.js` leaves the `npm ci` step cached.

The solution is in [solution.md](solution.md).
