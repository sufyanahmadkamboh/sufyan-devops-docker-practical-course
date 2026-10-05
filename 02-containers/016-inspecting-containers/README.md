# Lesson 016 · Inspecting containers

> Level 3 · Working with containers · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

`docker inspect` prints everything Docker knows about a container as JSON: its configuration (image, command,
environment, ports, mounts), its state (running or not, exit code, start and finish times, whether it was killed for
memory) and its network settings. It is the most precise answer to "what is this container, and what happened to it?".
`--format` extracts exactly the field you need.

## Visual

```text
 docker inspect web
 [
   {
     "Id": "8d1e44b2c9a0…",
     "Name": "/web",
     "State":           { "Status": "running", "ExitCode": 0, "OOMKilled": false, "StartedAt": "…", … },
     "Config":          { "Image": "nginx:1.30-alpine", "Cmd": [ "nginx", "-g", "daemon off;" ], "Env": [ … ] },
     "HostConfig":      { "PortBindings": { "80/tcp": [ { "HostPort": "8080" } ] }, "RestartPolicy": { … } },
     "Mounts":          [ … ],
     "NetworkSettings": { "Networks": { "bridge": { "IPAddress": "172.17.0.2", … } } }
   }
 ]
 --format '{{.State.Status}}'   →  running              (a path into the JSON, case-sensitive)
 --format '{{json .Config.Env}}' →  ["PATH=…","NGINX_VERSION=1.30.…"]
```

## Lab setup

<!-- test: contains=web -->
```bash
docker run -d --name web -p 8080:80 -e APP_ENV=staging --restart unless-stopped nginx:1.30-alpine > /dev/null
docker ps --format '{{.Names}}'
```

## Demonstration

The full document is long (around 250 lines). The beginning:

<!-- test: contains="Name": "/web"; output=head:12 -->
```bash
docker inspect web | grep -E '"(Id|Name|Status|Running|ExitCode|StartedAt|Image)"' | head -12
```

```text
        "Id": "0eab881c3a641b67353217221c1b128b4ad3efcbece25211ac3b6e770f48a632",
            "Status": "running",
            "Running": true,
            "ExitCode": 0,
            "StartedAt": "2026-10-05T10:49:21.116275486Z",
        "Image": "sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94",
        "Name": "/web",
                "Name": "unless-stopped",
                    "Name": "overlayfs"
            "Image": "nginx:1.30-alpine",
```

Pick single fields with `--format`:

<!-- test: contains=state: running; contains=APP_ENV=staging; output -->
```bash
docker inspect --format 'state: {{.State.Status}}, started: {{.State.StartedAt}}' web
docker inspect --format 'image: {{.Config.Image}}, command: {{json .Config.Cmd}}' web
docker inspect --format 'restart policy: {{.HostConfig.RestartPolicy.Name}}' web
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' web
```

```text
state: running, started: 2026-10-05T10:49:21.116275486Z
image: nginx:1.30-alpine, command: ["nginx","-g","daemon off;"]
restart policy: unless-stopped
APP_ENV=staging
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NGINX_VERSION=1.30.5
PKG_RELEASE=1
DYNPKG_RELEASE=1
NJS_VERSION=1.0.1
NJS_RELEASE=1
ACME_VERSION=0.4.1
```

`.Config.Env` contains your `-e APP_ENV=staging` **and** the variables defined by the image (`PATH`, `NGINX_VERSION`).
Published ports and the IP address:

<!-- test: contains=8080; output -->
```bash
docker inspect --format '{{json .HostConfig.PortBindings}}' web
docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}}: {{$net.IPAddress}}{{end}}' web
```

```text
{"80/tcp":[{"HostIp":"","HostPort":"8080"}]}
bridge: 172.17.0.2
```

## Command breakdown

| Command / template | Meaning |
|---|---|
| `docker inspect NAME` | everything about a container (also works for images, networks, volumes) |
| `--format '{{.A.B}}'` | one field; names are case-sensitive, as in the JSON |
| `{{json .X}}` | print a whole object or list as JSON |
| `{{range .List}}{{println .}}{{end}}` | one list entry per line |
| `{{range $k, $v := .Map}}…{{end}}` | loop over a map (networks, ports) |
| `.State.ExitCode`, `.State.Error`, `.State.OOMKilled` | why a container stopped |

## Hands-on lab

**Instructions.** Print, in one line, the name of `web`, its image, the host port bound to its port 80 and its restart
policy.

**Expected result.** `/web nginx:1.30-alpine 8080 unless-stopped`.

**Verification.**

<!-- test: contains=/web nginx:1.30-alpine 8080 unless-stopped -->
```bash
docker inspect --format '{{.Name}} {{.Config.Image}} {{(index (index .HostConfig.PortBindings "80/tcp") 0).HostPort}} {{.HostConfig.RestartPolicy.Name}}' web
```

`index MAP "KEY"` reads a key that contains characters like `/`; `index LIST 0` reads the first entry.

## Break it

A new service is deployed, and stops shortly after starting:

<!-- test: contains=Exited (3); output -->
```bash
docker run -d --name api alpine:3.23 sh -c '
  [ -n "$DB_URL" ] || { echo "fatal: DB_URL is not set" >&2; exit 3; }
  echo "connecting to $DB_URL"; sleep 300' > /dev/null
sleep 1
docker ps -a --filter name=^api$ --format '{{.Names}}: {{.Status}}'
```

```text
api: Exited (3) 1 second ago
```

## Troubleshoot it

Ask Docker how it ended. `ExitCode 3` means the application chose to exit (a crash by a signal would be 128 + n, like
137); `OOMKilled false` rules out memory:

<!-- test: contains=exit code 3; contains=OOM killed false; output -->
```bash
docker inspect --format 'exit code {{.State.ExitCode}}, OOM killed {{.State.OOMKilled}}, error "{{.State.Error}}", ran from {{.State.StartedAt}} to {{.State.FinishedAt}}' api
```

```text
exit code 3, OOM killed false, error "", ran from 2026-10-05T10:49:23.602362905Z to 2026-10-05T10:49:23.746326719Z
```

The application's own message is in its log, and its configuration in `inspect`:

<!-- test: contains=DB_URL is not set; output -->
```bash
docker logs api
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' api
```

```text
fatal: DB_URL is not set
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Root cause: the container received no `DB_URL` (only `PATH`). Investigation order for any stopped container: **status
and exit code** (`inspect`) → **the application's message** (`logs`) → **the configuration it got** (`inspect`).

## Fix it

Recreate the container with the variable (lesson 059 covers configuration in depth):

<!-- test: contains=connecting to postgres; retry=5 -->
```bash
docker rm -f api > /dev/null
docker run -d --name api -e DB_URL=postgres://db:5432/shop alpine:3.23 sh -c '
  [ -n "$DB_URL" ] || { echo "fatal: DB_URL is not set" >&2; exit 3; }
  echo "connecting to $DB_URL"; sleep 300' > /dev/null 2>&1 || true
sleep 1
docker ps --filter name=^api$ --format '{{.Names}}: {{.Status}}'
docker logs api
```

## Practice challenge

Write a one-line "container report" for every container on the engine (running or not): name, image, status, exit code
and restart count, using one `docker inspect` call.

<details>
<summary>Solution</summary>

<!-- test: contains=/web; contains=/api; output -->
```bash
docker inspect --format '{{.Name}} | {{.Config.Image}} | {{.State.Status}} | exit {{.State.ExitCode}} | restarts {{.RestartCount}}' $(docker ps -aq)
```

```text
/api | alpine:3.23 | running | exit 0 | restarts 0
/web | nginx:1.30-alpine | running | exit 0 | restarts 0
```

`docker inspect` accepts several containers and applies the template to each. `docker ps --format` can show some of
these fields too, but only `inspect` has all of them (exit code, OOM, restart count, environment).

</details>

## Real-world example

Monitoring reports that a container restarts every few minutes. `docker inspect --format '{{.RestartCount}}
{{.State.ExitCode}} {{.State.OOMKilled}}' worker` answers in one line: `14 137 true` means the kernel killed it for
exceeding its memory limit (lesson 098), `14 1 false` means the application itself fails, and its logs will say why.
Kubernetes shows the same facts in `kubectl describe pod` as "Last State: Terminated, Reason: OOMKilled".

## Recap

- `docker inspect` is the full truth about a container: configuration, state, networking.
- `--format` with Go templates extracts fields; `json`, `range` and `index` handle objects, lists and maps.
- For a stopped container: exit code and OOM flag (`inspect`), then the message (`logs`), then the configuration.
- Exit code below 128: the application exited; 128 + n: killed by signal n.

## Cleanup

<!-- test -->
```bash
docker rm -f web api > /dev/null
```

Next: [Lesson 017 · Image layers](../../03-images/017-image-layers/README.md)
