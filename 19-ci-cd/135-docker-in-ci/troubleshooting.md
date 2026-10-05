<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 135 · Docker in CI · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate changes the greeting and pushes without running the tests:

```bash
cd ~/docker-practice/lesson-135
sed 's|Hello from Node.js|Hi from Node.js|' server.js > server.new && mv server.new server.js
VERSION=1.1.0 bash ci.sh 2>&1
```

```text
...
  13 |     
  14 |     # the image that is shipped: no tests, no root
--------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c node --test" did not complete successfully: exit code: 1

View build details: docker-desktop://dashboard/build/default/default/gkkylrqte2d17p5g0i699zawx
```

## Troubleshoot it

The pipeline stopped at step 1: the `RUN node --test` step of the test stage failed, so `docker build` failed and
`set -e` ended the script. Nothing was pushed:

```bash
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

```text
{"name":"node-api","tags":["1.0.0"]}
```

To see the full test report, run the test stage alone with plain progress output, and look for the failing test:

```bash
cd ~/docker-practice/lesson-135
docker build --target test --progress=plain . 2>&1 | grep -E "not ok|expected|actual" | head -5
test "${PIPESTATUS[0]}" -eq 0
```

The test expected `Hello from Node.js` and got `Hi from Node.js`: the change broke the API's contract.

## Fix it

Either the change is wrong (revert it), or the contract really changes (update the test in the same commit). Here
the change was a mistake:

```bash
cd ~/docker-practice/lesson-135
sed 's|Hi from Node.js|Hello from Node.js|' server.js > server.new && mv server.new server.js
VERSION=1.1.0 bash ci.sh
```
