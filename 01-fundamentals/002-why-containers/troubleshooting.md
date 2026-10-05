<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 002 · Why containers? · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate "upgrades" the server by hand to a different Flask version and only tests on their laptop:

```bash
docker run --rm python:3.14-slim sh -c 'pip install -q flask==3.0.3 2>/dev/null; pip show flask | grep Version'
```

```text
Version: 3.0.3
```

## Troubleshoot it

Every hand-installed environment drifts: this "server" now has Flask 3.0.3, the tested build has 3.1.3. Bugs that only
happen in one environment come from exactly this. Compare the two environments:

```bash
docker run --rm cafe-api:1.0 pip show flask | grep Version
```

## Fix it

Never change a running environment by hand. Change the pinned version in `requirements.txt`, rebuild the image, test it,
and ship the new image: the version is recorded in Git and identical everywhere.

```bash
grep -i flask requirements.txt
```
