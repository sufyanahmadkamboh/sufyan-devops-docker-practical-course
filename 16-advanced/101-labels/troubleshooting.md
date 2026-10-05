<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 101 · Labels · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate cleans up the test environment of team payments, using the key spelling from a wiki page:

```bash
found=$(docker ps -q --filter label=Team=payments --filter label=env=test)
[ -n "$found" ] && docker rm -f $found || echo "nothing to remove"
```

```text
nothing to remove
```

`pay-api` is still running.

## Troubleshoot it

Filters compare keys and values **exactly**, case included: `Team` is not `team`. Look at the container's real
labels:

```bash
docker inspect --format '{{json .Config.Labels}}' pay-api
```

```text
{"env":"test","team":"payments"}
```

## Fix it

Use the exact key. Before deleting anything selected by a filter, list it first:

```bash
docker ps --filter label=team=payments --filter label=env=test --format '{{.Names}}'
docker container rm -f $(docker ps -q --filter label=team=payments --filter label=env=test) > /dev/null && echo "removed"
```

```text
pay-api
removed
```

Several `--filter label=…` options must **all** match. Teams avoid this class of error by writing label keys in one
place (a Compose file, a CI template) and in a reverse-DNS style (`com.example.team`), lowercase.
