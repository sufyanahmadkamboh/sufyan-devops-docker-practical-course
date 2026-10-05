#!/usr/bin/env bash
# make-secret.sh: create secrets/db_password.txt with a random password, once (an existing one is kept).
#
# The file is readable by every user of THIS computer (mode 644) because Compose mounts it into the containers as it
# is, and the API (user 65532) and PostgreSQL (user 70) must be able to read it. Its folder is private (700).
# Never commit it: secrets/ is in .gitignore.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p secrets && chmod 700 secrets
if [ -s secrets/db_password.txt ]; then
  echo "kept the existing secrets/db_password.txt"
else
  (umask 022 && head -c 32 /dev/urandom | base64 | tr -d '/+=\n' | head -c 32 > secrets/db_password.txt)
  echo "created secrets/db_password.txt"
fi
