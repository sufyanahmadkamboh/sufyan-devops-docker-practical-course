<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 072 · exec and run · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Pipe a command from your computer into a container: count the lines of `app.py` inside the API container with
`wc -l`, feeding it through standard input (`exec -T`).

## Solution

```bash
cd ~/docker-practice/lesson-072
docker compose exec -T api sh -c 'wc -l' < app.py | sed 's/$/ lines in app.py/'
```

```text
28 lines in app.py
```

Without `-T`, Compose allocates a terminal when you run it interactively, and input redirection does not mix well with
terminals. `-T` is how scripts and CI jobs run commands in containers (database dumps and restores work the same way).
