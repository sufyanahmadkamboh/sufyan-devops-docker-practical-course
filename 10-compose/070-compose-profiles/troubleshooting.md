<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 070 · Profiles · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Someone decides "the API needs test data" and makes it depend on `seed`:

```bash
cp compose.yaml compose.good.yaml
cp broken/compose.yaml compose.yaml
docker compose up -d 2>&1
```

```text
service "api" depends on undefined service "seed": invalid compose project
```

## Troubleshoot it

`depends on undefined service "seed"`: `seed` is in the file, but its profile is not active, so for this command it
does not exist, and a service that always starts cannot depend on it. With the profile active, the file is valid:

```bash
docker compose --profile seed config --services
```

```text
seed
api
redis
```

## Fix it

An always-on service should not depend on an optional one. Either remove the dependency, or mark it optional with
`required: false` (Compose then waits for `seed` only when it is part of the run):

```bash
cp compose.good.yaml compose.yaml
docker compose config --services
```

```text
api
redis
```

The original file has no dependency: `seed` is a job you run when you need it, `--profile seed`.
