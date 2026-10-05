<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 005 · Installing Docker · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"     # use docker without sudo; log out and in again
```

## Demonstration

```bash
docker version --format 'Client: {{.Client.Version}} {{.Client.Os}}/{{.Client.Arch}}{{"\n"}}Server: {{.Server.Version}} {{.Server.Os}}/{{.Server.Arch}}'
```

```bash
docker info --format 'engine {{.ServerVersion}} on {{.OperatingSystem}} ({{.OSType}}/{{.Architecture}})
CPUs: {{.NCPU}}, memory: {{.MemTotal}} bytes
storage driver: {{.Driver}}, data in {{.DockerRootDir}}
containers: {{.Containers}}, images: {{.Images}}'
```

```bash
docker run --rm hello-world | head -3
```

## Hands-on lab

```bash
docker info --format '{{.ServerVersion}} {{.Driver}} {{.LoggingDriver}}'
```

## Break it

```bash
docker info --format '{{.ServerVersoin}}'
```

## Troubleshoot it

```bash
docker info --format '{{json .}}' | grep -o '"Server[A-Za-z]*"' | sort -u
```

## Fix it

```bash
docker info --format '{{.ServerVersion}}'
```

## Practice challenge

```bash
echo "client $(docker version --format '{{.Client.Version}}'), server $(docker info --format '{{.ServerVersion}}'), $(docker info --format '{{.ContainersRunning}} running, {{.Images}} images')"
```
