<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 013 · Running multiple containers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A cleanup script stops every container of a project. Run it for a project that has no containers:

```bash
docker stop $(docker ps -q --filter label=project=lesson-999) 2>&1
```

```text
docker: 'docker stop' requires at least 1 argument

Usage:  docker stop [OPTIONS] CONTAINER [CONTAINER...]

See 'docker stop --help' for more information
```

## Troubleshoot it

`'docker stop' requires at least 1 argument`: the filter matched nothing, so `$(…)` expanded to nothing and the command
became plain `docker stop`. Run the inner command alone to see what it returns:

```bash
echo "matches: $(docker ps -q --filter label=project=lesson-999 | wc -l | tr -d ' ')"
```

## Fix it

Only call `docker stop` when there is something to stop:

```bash
ids=$(docker ps -q --filter label=project=lesson-999)
if [ -n "$ids" ]; then docker stop $ids; else echo "nothing to stop"; fi
```

(`docker ps -q … | xargs -r docker stop` does the same with GNU `xargs`.)
