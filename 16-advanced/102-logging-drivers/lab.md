<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 102 · Logging drivers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a second chatty container with rotation: at most 3 files of 1 MB. Wait a few seconds and
show that `docker logs` holds only the most recent lines, while the unrotated `chatty` kept all 50,000.

**Expected result.** `rotated` keeps fewer lines (the oldest were rotated away, so its first line is not `line 1`);
`chatty` keeps 50,000.

**Verification.**

```bash
docker run -d --name rotated --log-opt max-size=1m --log-opt max-file=3 alpine:3.23 \
  sh -c 'pad=$(printf "%0100d" 0); i=0; while [ $i -lt 50000 ]; do i=$((i+1)); echo "line $i $pad"; done; sleep 300' > /dev/null
sleep 5
echo "rotated: $(docker logs rotated 2>&1 | wc -l) lines kept (first kept: $(docker logs rotated 2>&1 | head -1))"
echo "chatty:  $(docker logs chatty 2>&1 | wc -l) lines kept"
docker inspect --format '{{json .HostConfig.LogConfig.Config}}' rotated
```
