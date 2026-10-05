#!/usr/bin/env bash
# ci.sh: the pipeline of lesson 135, runnable on any computer with Docker.
#   1 test     build the test stage: the unit tests run inside the build
#   2 build    build the production image, tagged with an immutable version
#   3 smoke    start the image and check that it answers
#   4 push     push it to the registry (only reached when 1-3 passed)
#
#   VERSION=1.0.0 REGISTRY=localhost:5000 bash ci.sh
set -euo pipefail

version="${VERSION:?set VERSION, for example the Git commit: VERSION=\$(git rev-parse --short HEAD)}"
image="${REGISTRY:-localhost:5000}/node-api:$version"

echo "== 1/4 test"
docker build -q --target test -t node-api:test . > /dev/null

echo "== 2/4 build $image"
docker build -q --target production -t "$image" . > /dev/null

echo "== 3/4 smoke test"
docker run -d --name smoke "$image" > /dev/null
trap 'docker rm -f smoke > /dev/null 2>&1' EXIT
for _ in $(seq 1 20); do
  if docker exec smoke node -e "fetch('http://127.0.0.1:3000/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"; then
    ok=1
    break
  fi
  sleep 1
done
[ "${ok:-}" = 1 ] || { echo "smoke test failed: the container did not answer"; docker logs smoke; exit 1; }

echo "== 4/4 push"
docker push -q "$image"
echo "pipeline passed: $image"
