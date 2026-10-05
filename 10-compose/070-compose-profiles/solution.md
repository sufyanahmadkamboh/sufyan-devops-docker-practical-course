<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 070 · Profiles · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Run the `seed` job once more, as a one-off container that is removed afterwards, without starting the `debug`
profile, and check that the counter is reset to 100.

## Solution

```bash
cd ~/docker-practice/lesson-070
docker compose run --rm seed 2> /dev/null
curl -s localhost:8080/visits
```

```text
OK
{"visits":101}
```

`docker compose run SERVICE` starts one service even when its profile is not active; `--rm` removes it after it exits.
`OK` is Redis's answer to `SET`.
