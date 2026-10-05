#!/bin/sh
# Refuses to start without its configuration, like most real services.
if [ -z "$GREETING" ]; then
  echo "ERROR: GREETING is not set" >&2
  exit 1
fi
echo "greeter started: $GREETING"
exec sleep 3600
