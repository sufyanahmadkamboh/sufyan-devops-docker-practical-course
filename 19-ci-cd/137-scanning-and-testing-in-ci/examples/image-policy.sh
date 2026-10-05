#!/usr/bin/env bash
# image-policy.sh IMAGE: the policy gate of lesson 137. Checks the rules every image must follow before it is
# pushed, prints PASS/FAIL per rule, and exits with 1 if any rule fails (so `set -e` stops the pipeline).
#
#   bash image-policy.sh node-api:1.0.0
#   MAX_MB=100 bash image-policy.sh node-api:1.0.0      (a stricter size budget)
set -euo pipefail

image="${1:?usage: image-policy.sh IMAGE}"
max_mb="${MAX_MB:-300}"
failed=0

check() {   # check RULE RESULT: RESULT is "ok" or the reason it failed
  if [ "$2" = ok ]; then echo "PASS  $1"; else echo "FAIL  $1: $2"; failed=1; fi
}

docker image inspect "$image" > /dev/null 2>&1 || { echo "FAIL  image $image not found"; exit 1; }

# 1 a version tag, never latest (or no tag, which means latest)
name="${image##*/}"
case "$name" in
  *:latest) r="tag it with a version, not latest" ;;
  *:*) r=ok ;;
  *) r="no tag means latest: tag it with a version" ;;
esac
check "version tag" "$r"

# 2 not root
user=$(docker image inspect "$image" --format '{{.Config.User}}')
case "$user" in "" | root | 0 | 0:*) r="runs as root (set USER)" ;; *) r=ok ;; esac
check "non-root user" "$r"

# 3 a healthcheck
hc=$(docker image inspect "$image" --format '{{if .Config.Healthcheck}}yes{{end}}')
[ "$hc" = yes ] && r=ok || r="no HEALTHCHECK"
check "healthcheck" "$r"

# 4 no secret-looking environment variables baked into the image
secrets=$(docker image inspect "$image" --format '{{range .Config.Env}}{{println .}}{{end}}' |
  cut -d= -f1 | grep -Ei 'PASSWORD|SECRET|TOKEN|API_KEY' | tr '\n' ' ' || true)
[ -z "$secrets" ] && r=ok || r="secret-like variables: $secrets"
check "no secrets in ENV" "$r"

# 5 a size budget
mb=$(( $(docker image inspect "$image" --format '{{.Size}}') / 1024 / 1024 ))
[ "$mb" -le "$max_mb" ] && r=ok || r="$mb MB > $max_mb MB"
check "size ($mb MB, budget $max_mb MB)" "$r"

exit "$failed"
