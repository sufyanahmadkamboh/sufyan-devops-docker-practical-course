<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 050 · Container DNS · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Stop `search-1` and look up `search` again. What does DNS return now, and what does that mean for clients?

## Solution

```bash
docker stop search-1 > /dev/null
count=$(docker run --rm --network shop-net busybox:1.37 nslookup search 2>&1 | grep '^Address' | grep -vc 127.0.0.11)
[ "$count" -eq 1 ] && echo "one address: only the running search-2"
```

```text
one address: only the running search-2
```

Docker's DNS only returns running containers, so clients that resolve the name again are sent to `search-2`. Clients
that cached the old address still fail: DNS round-robin is not a health-checked load balancer (Compose and Kubernetes
services build on the same idea with more care).
