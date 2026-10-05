# Writing lessons for this course

Every lesson is one `README.md` that a learner follows from top to bottom, and that `tests/run.sh` runs exactly as the
learner types it. The lessons of [module 01](../01-fundamentals) are the reference: copy their structure, tone and
level of detail.

## Lesson folder

```text
NN-module/
├── assessment.md                knowledge check, practical task, troubleshooting task, real-world scenario
└── 0NN-lesson-slug/
    ├── README.md                the lesson (the only file you write by hand)
    ├── examples/                files the lesson needs: before/ broken/ fixed/ final/ where useful
    ├── lab.md  troubleshooting.md  challenge.md  solution.md  commands.md
    └──                          ↑ generated from README.md: python tools/lesson_files.py
```

## README.md structure

The headings are fixed (the generator and the module pages depend on them), in this order:

```text
# Lesson NNN · Title

> Level N · Level name · ⏱ NN minutes · run every command from the course folder

## What are we learning?        the concept in a few sentences: what it is, why it matters
## Visual                       an ASCII diagram (```text), plus a table where it helps
## Lab setup                    bash scripts/lab.sh lesson-NNN SOURCE...  then  cd ~/docker-practice/lesson-NNN
## Demonstration                real commands with their real output (```text blocks written by --update)
## Command breakdown            a table: command / flag → meaning (with lesson references)
## Hands-on lab                 **Instructions.** / **Expected result.** / **Verification.** + a tested block
## Break it                     an intentional, realistic failure, with its real error output
## Troubleshoot it              read the error, investigate with commands, explain the root cause
## Fix it                       the fix, and a block that verifies it
## Practice challenge           a task; the tested solution inside <details><summary>Solution</summary> … </details>
## Real-world example           how teams use this in practice (no invented numbers or companies)
## Recap                        3–5 bullets
## Cleanup                      remove what the lesson created (containers, images built, networks, volumes, labs)

Next: [Lesson NNN · Title](../0NN-slug/README.md)
```

## Test annotations

Every ```` ```bash ```` block runs, in order, in one shell session (the working directory carries over, variables do
not). Put an annotation on the line before a block:

| Annotation | Meaning |
|---|---|
| `<!-- test: contains=TEXT -->` | must succeed and print TEXT (`contains=a; contains=b` for several) |
| `<!-- test: anyof=A\|\|B -->` | output contains A or B (for registry errors that may also be a rate limit) |
| `<!-- test: fail; contains=TEXT -->` | must fail (Break it), printing TEXT |
| `<!-- test: absent=TEXT -->` | must not print TEXT |
| `<!-- test: output -->` | `--update` writes the real output into the ```` ```text ```` block that follows |
| `<!-- test: retry=N -->` | retry up to N times, 2 s apart (waiting for a server to start); read-only blocks only |
| `<!-- test: skip -->` | never run (installation steps, illustrations, interactive commands) |
| `<!-- test: github -->` | needs GitHub credentials: runs only with `MDRUN_GITHUB=1` |

Rules:

- **Never write output by hand.** Add `output`, run `bash tests/run.sh --update FILE`, and read what it recorded. If
  the output is different from what the text says, fix the text.
- Errors stay visible: a Break it block prints the real error (`2>&1` where Docker writes to stderr).
- Each block checks something meaningful (`contains=`), not just "it exited 0".
- A server started with `-d` is not ready immediately: query it in a separate block with `retry=10`.
- Every lesson must pass on its own: `bash tests/run.sh FILE` starts from an empty engine (images stay cached).
- Use `docker run --rm` for one-off commands; name long-running containers after the lesson topic and remove them in
  Cleanup. Remove images the lesson builds (`docker image rm -f NAME:TAG`).
- Use only the pinned images of [scripts/prefetch-images.sh](../scripts/prefetch-images.sh), always with their tag.
  Do not pull other images from Docker Hub (anonymous pulls are rate-limited); `docker image pull` of a cached image
  still contacts Docker Hub, so guard it: `docker image inspect IMG > /dev/null 2>&1 || docker image pull IMG`.
- Host ports: use 8080–8099 for lesson servers, 5000 for the local registry; publish to `127.0.0.1` only when a lesson
  is about that.
- Bind mounts: `-v "$(pwd)/file:/path"`. The runner sets `MSYS_NO_PATHCONV=1` so this works in Git Bash on Windows.
- Host commands must work in Git Bash, macOS and Linux: `curl`, `grep`, `sed`, `tr`, `head`, `tail`, `printf`. Avoid
  `jq`, `watch`, `timeout`, GNU-only flags; use `docker … --format` instead of parsing tables.
- Never put real credentials in a lesson. Secrets in examples are obviously fake (`example-password-change-me`).
- Write for beginners: explain every new flag once, link to the lesson that covers it in depth.

## Lesson numbers and folders

The `Next:` link of the last lesson of a module points to the first lesson of the next module.

| Module | Lessons |
|---|---|
| 01-fundamentals | 001-what-is-docker, 002-why-containers, 003-docker-vs-vms, 004-docker-architecture, 005-installing-docker |
| 02-containers | 006-first-container, 007-images-vs-containers, 008-listing-containers, 009-container-lifecycle, 010-container-names, 011-running-nginx, 012-port-mapping, 013-multiple-containers, 014-container-logs, 015-exec-into-containers, 016-inspecting-containers |
| 03-images | 017-image-layers, 018-pulling-images, 019-listing-and-removing-images, 020-image-tags, 021-latest-tag-danger |
| 04-dockerfiles | 022-first-dockerfile, 023-from, 024-workdir, 025-copy-and-add, 026-run, 027-cmd, 028-entrypoint, 029-cmd-and-entrypoint, 030-env, 031-arg, 032-expose, 033-user, 034-dockerfile-best-practices |
| 05-builds | 035-docker-build, 036-build-context, 037-dockerignore, 038-build-layers, 039-build-cache |
| 06-application-containerization | 040-containerize-node, 041-containerize-python, 042-containerize-go, 043-containerize-java, 044-containerize-php, 045-comparing-stacks |
| 07-networking | 046-networking-fundamentals, 047-default-bridge, 048-custom-networks, 049-container-to-container, 050-container-dns, 051-expose-vs-publish, 052-network-troubleshooting |
| 08-storage | 053-writable-layer, 054-bind-mounts, 055-named-volumes, 056-inspecting-volumes, 057-volumes-vs-bind-mounts, 058-persistent-database |
| 09-environment-config | 059-environment-variables, 060-env-files, 061-config-vs-secrets |
| 10-compose | 062-why-compose, 063-first-compose-file, 064-compose-services, 065-compose-networking, 066-compose-volumes, 067-compose-environment, 068-depends-on-vs-readiness, 069-compose-healthchecks, 070-compose-profiles, 071-compose-logs, 072-compose-exec, 073-compose-build, 074-compose-up-down |
| 11-registry | 075-what-is-a-registry, 076-docker-hub, 077-image-naming, 078-private-registries, 079-github-container-registry |
| 12-security | 080-attack-surface, 081-non-root-users, 082-image-security, 083-secrets-in-images, 084-read-only-filesystems, 085-linux-capabilities, 086-resource-limits-for-security |
| 13-multistage | 087-why-multistage, 088-multistage-node, 089-multistage-go, 090-multistage-java, 091-measuring-image-size |
| 14-observability | 092-healthcheck, 093-running-is-not-healthy, 094-logs-in-depth, 095-docker-stats, 096-docker-events |
| 15-resources | 097-cpu-limits, 098-memory-limits, 099-memory-pressure |
| 16-advanced | 100-metadata-and-inspect, 101-labels, 102-logging-drivers, 103-buildx, 104-multi-architecture-images, 105-cache-optimization |
| 17-troubleshooting | 25 problems, `NN-slug/README.md` (referred to as "troubleshooting problem NN") |
| 18-production | 130-production-dockerfile, 131-container-design, 132-immutable-containers, 133-production-configuration, 134-security-review |
| 19-ci-cd | 135-docker-in-ci, 136-build-and-push-with-github-actions, 137-scanning-and-testing-in-ci |
| 20-kubernetes | 138-from-docker-to-kubernetes, 139-deploy-an-image-to-kind, 140-kubernetes-for-docker-users |

Troubleshooting problems (17-troubleshooting): 01 container exits immediately, 02 wrong command, 03 wrong image,
04 port already in use, 05 application not reachable, 06 listening on localhost, 07 wrong container port,
08 wrong network, 09 DNS failure, 10 database connection failure, 11 missing environment variable, 12 permission
denied, 13 cannot write files, 14 volume not mounted, 15 data disappeared, 16 build failure, 17 unexpected cache,
18 huge image, 19 Dockerfile security issue, 20 running as root, 21 healthcheck failure, 22 memory limit exceeded,
23 CPU throttling, 24 registry authentication failure, 25 image pull failure.

## Module assessment

`NN-module/assessment.md`, tested like a lesson:

```text
# Module NN assessment · Name
## Knowledge check          5–10 questions, each answer in <details>
## Practical task           a task built on the module; tested solution in <details>
## Troubleshooting task     a prepared broken setup (examples/ of the module or a lab); tested diagnosis and fix
## Real-world scenario      a short situation; a model answer in <details>
## Cleanup
```

## Running the tests

```bash
bash tests/run.sh --update NN-module/0NN-*/README.md      # one lesson, recording outputs
bash tests/run.sh NN-module/*/README.md NN-module/assessment.md
python tools/lesson_files.py                              # regenerate lab.md, challenge.md, …
python tests/check_links.py                               # every relative link resolves
```

Only one test run uses the engine at a time (`tests/.lock`). Docker commands you try by hand must hold the same lock,
because each run empties the engine: `bash tests/locked.sh bash -c 'docker …'`.
