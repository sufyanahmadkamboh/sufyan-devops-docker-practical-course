<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 049 · Container-to-container communication · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show that Redis really holds the counter: read the key `visits` with `redis-cli` inside the `redis`
container, then call the API once more and read it again.

**Expected result.** The value grows by one.

**Verification.**

```bash
echo "before: $(docker exec redis redis-cli get visits)"
curl -s http://localhost:8080/visits > /dev/null
echo "after:  $(docker exec redis redis-cli get visits)"
```
