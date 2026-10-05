<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 050 · Container DNS · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show that the embedded DNS also resolves external names, by looking up `example.com` from a
container on `shop-net`, and that `search` resolves to the two addresses of `search-1` and `search-2`.

**Expected result.** An address for `example.com`, and the same two addresses as
`docker inspect search-1 search-2`.

**Verification.**

```bash
docker run --rm --network shop-net busybox:1.37 nslookup example.com 2>&1 | grep -m1 -A1 '^Name'
for c in search-1 search-2; do
  echo "$c $(docker inspect $c --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')"
done
```
