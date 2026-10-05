<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 097 · CPU limits · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate copies a production setting to their laptop:

```bash
docker run --rm --cpus 64 alpine:3.23 true 2>&1
```

```text
docker: Error response from daemon: range of CPUs is from 0.01 to 14.00, as there are only 14 CPUs available

Run 'docker run --help' for more information
```

## Troubleshoot it

The engine refuses limits it cannot provide, and says what is possible: from 0.01 to the number of CPUs the engine
has. Ask the engine how many it has (on Docker Desktop, the VM's CPUs, configurable in its settings):

```bash
echo "engine CPUs: $(docker info --format '{{.NCPU}}')"
```

```text
engine CPUs: 14
```

## Fix it

Use a limit within that range. A portable choice for development is a fraction of what the machine has:

```bash
docker run --rm --cpus 1 alpine:3.23 sh -c 'echo "cpu.max: $(cat /sys/fs/cgroup/cpu.max)"'
```

```text
cpu.max: 100000 100000
```
