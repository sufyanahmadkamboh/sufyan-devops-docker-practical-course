<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 005 · Installing Docker · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A typo in a field name:

```bash
docker info --format '{{.ServerVersoin}}'
```

```text

template: :1:2: executing "" at <.ServerVersoin>: can't evaluate field ServerVersoin in type system.dockerInfo
```

## Troubleshoot it

`can't evaluate field ServerVersoin`: the template is valid, but `docker info` has no field of that name. Field names
are case-sensitive and spelled exactly as in the JSON form of the report. List the fields that start with `Server`:

```bash
docker info --format '{{json .}}' | grep -o '"Server[A-Za-z]*"' | sort -u
```

```text
"ServerVersion"
```

## Fix it

```bash
docker info --format '{{.ServerVersion}}'
```

Other installation problems and their fixes:

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` | engine not running | start Docker Desktop / `sudo systemctl start docker` |
| `permission denied … docker.sock` | Linux user not in the `docker` group | `sudo usermod -aG docker "$USER"`, then log in again |
| `docker: command not found` | CLI not installed or not on `PATH` | reinstall; open a new terminal |
| `WSL 2 installation is incomplete` | Windows feature missing | `wsl --install` in an administrator PowerShell, reboot |
