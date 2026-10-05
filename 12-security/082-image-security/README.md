# Lesson 082 · Image security: trusted, minimal, pinned, scanned

> Level 13 · Container security · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Your image is only as secure as everything inside it, and most of what is inside comes from the base image. Four habits
keep it under control:

1. **Trusted**: start from official images or verified publishers, never a random repository.
2. **Minimal**: the fewer packages, the fewer vulnerabilities and tools for an attacker (`-slim`, `alpine`, distroless).
3. **Pinned**: a tag can be moved to a different image; a **digest** (`@sha256:…`) cannot.
4. **Scanned**: a scanner compares the packages in the image with databases of known vulnerabilities (CVEs).

## Visual

```text
  Trusted                      Minimal                      Pinned                         Scanned
  ┌───────────────────────┐    python:3.14         big      python:3.14-slim               docker scout cves IMAGE
  │ Docker Official Image │    python:3.14-slim     │         (a tag: can move)            trivy image IMAGE
  │ Verified Publisher    │    python:3.14-alpine   │           ▼                              │
  │ your own registry     │    distroless          small    python@sha256:c3e5…              ▼
  └───────────────────────┘    fewer packages =             (a digest: always the          CVEs per package
     ✗ someuser/python-fast    fewer CVEs and tools          same bytes)                   → update the base
```

## Lab setup

No files are needed: this lesson inspects images that are already on your computer.

## Demonstration

**Minimal.** The same language runtime in different variants (sizes as stored on this engine):

<!-- test: contains=python:3.14-slim; output -->
```bash
for image in python:3.14-slim python:3.14-alpine gcr.io/distroless/static-debian12:nonroot; do
  echo "$image $(docker image inspect --format '{{.Size}}' "$image" | awk '{printf "%.1f MB", $1/1000000}')"
done
```

```text
python:3.14-slim 46.5 MB
python:3.14-alpine 20.4 MB
gcr.io/distroless/static-debian12:nonroot 0.7 MB
```

The distroless image has no shell to look around with: list its files from the outside instead, with `docker export`
(the file system of a container, as a tar stream). The container is only created, never started, so the command given
to `docker create` (`nothing-to-run`, the image has no default command) never runs:

<!-- test: contains=etc/passwd; contains=no shell; output -->
```bash
docker create --name peek gcr.io/distroless/static-debian12:nonroot nothing-to-run > /dev/null
echo "$(docker export peek | tar -t | grep -vc '/$') files, for example:"
docker export peek | tar -t | grep -E '^etc/(passwd|group|ssl/certs/ca-certificates.crt)$'
docker export peek | tar -t | grep -E 'bin/(sh|bash|busybox)$' || echo "no shell in the image"
docker rm peek > /dev/null
```

```text
1340 files, for example:
etc/group
etc/passwd
etc/ssl/certs/ca-certificates.crt
no shell in the image
```

**What a scanner looks at.** Every package with its exact version. Here, the TLS library of the Alpine image:

<!-- test: contains=libcrypto3; output -->
```bash
docker run --rm alpine:3.23 apk list --installed 2>/dev/null | grep -E '^(libcrypto3|libssl3|musl)-'
```

```text
libcrypto3-3.5.8-r0 x86_64 {openssl} (Apache-2.0) [installed]
libssl3-3.5.8-r0 x86_64 {openssl} (Apache-2.0) [installed]
musl-1.2.5-r23 x86_64 {musl} (MIT) [installed]
musl-utils-1.2.5-r23 x86_64 {musl} (MIT AND BSD-2-Clause AND GPL-2.0-or-later) [installed]
```

A scanner checks each of these versions against vulnerability databases and reports the known CVEs, with the version
that fixes them.

**Pinned.** A tag is a movable name; the digest identifies the exact content:

<!-- test: contains=alpine@sha256:; output -->
```bash
docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23
```

```text
alpine@sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
```

<!-- test: contains=VERSION_ID; output -->
```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
docker run --rm "$digest" grep VERSION_ID /etc/os-release
```

```text
VERSION_ID=3.23.6
```

`FROM alpine:3.23@sha256:…` in a Dockerfile builds from exactly that image, even if someone re-tags `3.23` tomorrow.

**Scanned.** Docker Scout is part of Docker Desktop and needs a (free) Docker account; Trivy is an open-source scanner
that runs as a container. Both list the CVEs of an image by severity:

<!-- test: skip -->
```bash
docker scout quickview alpine:3.23              # summary per severity; docker login first
docker scout cves --only-severity critical,high alpine:3.23
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image alpine:3.23
```

Without a login, Docker Scout stops with a request to sign in: scanning is an online service that needs its CVE
database.

## Command breakdown

| Command / syntax | What it does |
|---|---|
| `docker image inspect --format '{{.Size}}' IMG` | the image's size in bytes |
| `docker export CONTAINER \| tar -t` | list every file of a container, even without a shell inside |
| `apk list --installed` / `dpkg -l` | the packages and versions a scanner checks |
| `docker image inspect --format '{{index .RepoDigests 0}}'` | the image's digest reference `repo@sha256:…` |
| `IMAGE@sha256:DIGEST` | refer to an image by content, not by tag |
| `docker scout cves IMG` / `trivy image IMG` | list known vulnerabilities |

## Hands-on lab

**Instructions.** Get the digest reference of `python:3.14-slim` and run `python --version` from it by digest.

**Expected result.** `Python 3.14…`, from an image referenced as `python@sha256:…`.

**Verification.**

<!-- test: contains=Python 3.14 -->
```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.14-slim)
echo "$digest"
docker run --rm "$digest" python --version
```

## Break it

Copy a digest from a chat message and lose half of it on the way:

<!-- test: fail; contains=invalid reference format; output -->
```bash
docker run --rm alpine@sha256:85fe1e81d6758c208f3e1eed 2>&1
```

```text
docker: invalid reference format

Run 'docker run --help' for more information
```

## Troubleshoot it

`invalid reference format`: Docker did not even contact a registry. A digest reference must be exactly
`name@sha256:` followed by **64** hexadecimal characters. Count them:

<!-- test: contains=24; output -->
```bash
printf '%s' 85fe1e81d6758c208f3e1eed | wc -c
```

```text
24
```

24 characters, so the reference is truncated. A digest is never typed by hand: copy it from the source of truth.

## Fix it

Read the digest from the image (or from the registry, `docker buildx imagetools inspect IMAGE`) and use it unchanged:

<!-- test: contains=64 -->
```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
echo "${digest#*sha256:}" | tr -d '\n' | wc -c
docker run --rm "$digest" true && echo "digest reference works"
```

## Practice challenge

Write the first line of a Dockerfile that pins `python:3.14-slim` to its digest while keeping the tag readable for
humans (`FROM name:tag@sha256:…`), then build an image from it to prove it works.

<details>
<summary>Solution</summary>

<!-- test: contains=pinned:1.0; output -->
```bash
mkdir -p ~/docker-practice/lesson-082 && cd ~/docker-practice/lesson-082
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.14-slim)
printf 'FROM python:3.14-slim@%s\nCMD ["python", "--version"]\n' "${digest#*@}" > Dockerfile
head -1 Dockerfile | cut -c1-40
docker build -q -t pinned:1.0 . > /dev/null && docker image ls pinned --format '{{.Repository}}:{{.Tag}}'
```

```text
FROM python:3.14-slim@sha256:c3e521df8b2
pinned:1.0
```

When both are given, Docker uses the digest; the tag is documentation. Tools such as Dependabot or Renovate update the
digest when a new base image is published, through a reviewed pull request.

</details>

## Real-world example

A team pins every base image by digest and lets a bot open a pull request whenever the upstream image changes. CI
builds the image, scans it and fails the pipeline on critical vulnerabilities that have a fix available. Production
therefore only receives base image updates that were built, scanned and reviewed, and a rebuild never silently picks up
a different base.

## Recap

- Use official or verified base images; prefer the smallest variant that works (`-slim`, `alpine`, distroless).
- A tag can move; a digest (`@sha256:` + 64 hex characters) always means the same bytes.
- Scanners compare the installed package versions against CVE databases; rebuild on fixed base images regularly.
- `docker export` inspects images that have no shell.

## Cleanup

<!-- test -->
```bash
docker image rm -f pinned:1.0 > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-082
```

Next: [Lesson 083 · Secrets in images](../083-secrets-in-images/README.md)
