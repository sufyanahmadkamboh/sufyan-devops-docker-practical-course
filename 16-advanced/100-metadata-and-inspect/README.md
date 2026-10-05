# Lesson 100 · Metadata and docker inspect

> Level 17 · Advanced Docker · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Every Docker object (image, container, network, volume) has a JSON document with everything the engine knows about
it. `docker inspect` prints it, and `--format` with Go templates extracts exactly the fields you need, for scripts,
for debugging, and for audits. Lesson 016 introduced it; this lesson shows how to navigate the document, the template
functions that matter, and the difference between an **image's** and a **container's** metadata.

## Visual

```text
  image metadata (docker image inspect)           container metadata (docker container inspect)
  ┌───────────────────────────────────┐           ┌────────────────────────────────────────────┐
  │ Id, RepoTags, RepoDigests         │           │ Id, Name, Image, Created, RestartCount     │
  │ Architecture, Os, Size            │           │ State      Status, ExitCode, OOMKilled,    │
  │ Config     Env, Cmd, Entrypoint,  │──defaults─▶│            Health, StartedAt               │
  │            ExposedPorts, User,    │           │ Config     what this container runs with   │
  │            Labels, Healthcheck    │           │ HostConfig limits, ports, mounts, caps     │
  │ RootFS     Layers                 │           │ Mounts     volumes and bind mounts         │
  └───────────────────────────────────┘           │ NetworkSettings  Networks, IPAddress, Ports│
                                                  └────────────────────────────────────────────┘
  docker inspect --format '{{.State.Status}}'  ·  '{{json .Config.Env}}'  ·  '{{range …}}…{{end}}'
```

## Lab setup

No files are needed: this lesson inspects an nginx container.

<!-- test: contains=started web -->
```bash
docker network create shop-net > /dev/null
docker volume create shop-data > /dev/null
docker run -d --name web --network shop-net -p 8080:80 -v shop-data:/data -e APP_ENV=staging --memory 128m \
  nginx:1.30-alpine > /dev/null && echo "started web"
```

## Demonstration

The top-level keys of a container's document:

<!-- test: contains=HostConfig; contains=NetworkSettings; output -->
```bash
docker container inspect web | grep -E '^        "[A-Za-z]+": ' | cut -d'"' -f2 | tr '\n' ' '; echo
```

```text
Id Created Path Args State Image ResolvConfPath HostnamePath HostsPath LogPath Name RestartCount Driver Platform MountLabel ProcessLabel AppArmorProfile ExecIDs HostConfig Storage Mounts Config NetworkSettings ImageManifestDescriptor 
```

Single values with `--format`:

<!-- test: contains=running; contains=134217728; output -->
```bash
docker inspect --format 'status={{.State.Status}} started={{.State.StartedAt}}' web
docker inspect --format 'image={{.Config.Image}} memory={{.HostConfig.Memory}}' web
```

```text
status=running started=2026-10-05T17:01:31.852674192Z
image=nginx:1.30-alpine memory=134217728
```

Lists and maps, with `range`, `json` and `index`:

<!-- test: contains=APP_ENV=staging; contains=shop-net; contains=shop-data; output -->
```bash
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' web | grep APP_ENV
docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{end}}' web
docker inspect --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}' web
docker inspect --format '{{json .NetworkSettings.Ports}}' web
docker inspect --format '{{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' web
```

```text
APP_ENV=staging
shop-net 172.18.0.2
volume shop-data -> /data
{"80/tcp":[{"HostIp":"0.0.0.0","HostPort":"8080"},{"HostIp":"::","HostPort":"8080"}]}
8080
```

The container inherited its command and exposed port from the **image's** configuration:

<!-- test: contains=nginx; output -->
```bash
docker image inspect --format 'Cmd={{json .Config.Cmd}} Exposed={{json .Config.ExposedPorts}} Layers={{len .RootFS.Layers}}' nginx:1.30-alpine
```

```text
Cmd=["nginx","-g","daemon off;"] Exposed={"80/tcp":{}} Layers=8
```

## Command breakdown

| Template | Meaning |
|---|---|
| `{{.A.B}}` | field B inside A (names are case-sensitive) |
| `{{json .X}}` | X as JSON (for lists and maps) |
| `{{range .List}}{{.Field}}{{end}}` | repeat for every element |
| `{{range $k, $v := .Map}}{{$k}}={{$v}}{{end}}` | repeat for every key of a map |
| `{{index .Map "key"}}` | a map value whose key has special characters (`80/tcp`) |
| `{{len .List}}` | number of elements |
| `{{println .}}` | the value and a line break |
| `docker inspect --type image NAME` | inspect the image even if a container has the same name |

## Hands-on lab

**Instructions.** With one `docker inspect --format` command, print the container's restart policy, its memory limit
in bytes, and the host port of `80/tcp`.

**Expected result.** `restart=no memory=134217728 port=8080`.

**Verification.**

<!-- test: contains=restart=no memory=134217728 port=8080 -->
```bash
docker inspect --format 'restart={{.HostConfig.RestartPolicy.Name}} memory={{.HostConfig.Memory}} port={{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' web
```

## Break it

A script that worked for containers is pointed at an image:

<!-- test: fail; anyof=map has no entry for key||can't evaluate field; output -->
```bash
docker inspect --format '{{.State.Status}}' nginx:1.30-alpine 2>&1
```

```text

template parsing error: template: :1:8: executing "" at <.State.Status>: map has no entry for key "State"
```

## Troubleshoot it

`docker inspect NAME` looks the name up among containers, images, networks and volumes, and returns whichever it
finds. `nginx:1.30-alpine` is an image, and images have no `State`. Ask which type an object is, and look at the keys
the image document does have:

<!-- test: contains=RootFS; output -->
```bash
docker image inspect nginx:1.30-alpine | grep -E '^        "[A-Za-z]+": ' | cut -d'"' -f2 | tr '\n' ' '; echo
```

```text
Id RepoTags RepoDigests Comment Created Config Architecture Os Size RootFS Metadata Descriptor Identity 
```

## Fix it

Use the field that exists for the object you mean, and name the type explicitly so the script fails clearly when it
gets the wrong object:

<!-- test: contains=running; contains=amd64; output -->
```bash
docker container inspect --format '{{.State.Status}}' web
docker image inspect --format '{{.Os}}/{{.Architecture}}' nginx:1.30-alpine
```

```text
running
linux/amd64
```

`docker container inspect` refuses images (`No such container`), `docker image inspect` refuses containers: errors
instead of surprises.

## Practice challenge

Audit the host: for every running container, print its name, user, whether it is privileged, its memory limit and
whether its root file system is read-only, one line each (lessons 080–086).

<details>
<summary>Solution</summary>

<!-- test: contains=/web; output -->
```bash
docker ps -q | xargs docker inspect --format \
  '{{.Name}} user={{if .Config.User}}{{.Config.User}}{{else}}root{{end}} privileged={{.HostConfig.Privileged}} memory={{.HostConfig.Memory}} readonly={{.HostConfig.ReadonlyRootfs}}'
```

```text
/web user=root privileged=false memory=134217728 readonly=false
```

`{{if}}…{{else}}…{{end}}` handles the empty `User` field (empty means the image's default, root for nginx). Run on a
real host, this one line shows which containers ignore the security lessons.

</details>

## Real-world example

Deployment scripts use `docker inspect` to wait for health (`{{.State.Health.Status}}`), to find the address of a
service container in CI (`{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}`), and to verify that what runs is
what was deployed (`{{.Image}}` is the image ID the container was created from). Security tools run audits like the
challenge across fleets of hosts.

## Recap

- `docker inspect` prints the engine's JSON document for any object; `--format` extracts fields.
- Images describe defaults (`Config`, `RootFS`); containers add `State`, `HostConfig`, `Mounts`, `NetworkSettings`.
- `json`, `range`, `index`, `len`, `if` cover almost every need.
- Use `docker container inspect` / `docker image inspect` in scripts to get clear errors.

## Cleanup

<!-- test -->
```bash
docker rm -f web > /dev/null 2>&1 || true
docker volume rm shop-data > /dev/null 2>&1 || true
docker network rm shop-net > /dev/null 2>&1 || true
```

Next: [Lesson 101 · Labels](../101-labels/README.md)
