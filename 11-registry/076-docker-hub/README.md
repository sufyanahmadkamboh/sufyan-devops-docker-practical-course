# Lesson 076 · Docker Hub

> Level 12 · Registries · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Docker Hub (`docker.io`) is Docker's default registry: every image name without a registry address comes from there.
It hosts **official images** (`nginx`, `python`, `postgres`, maintained with Docker), images of verified publishers, and
every user's and organisation's own repositories. To push, you log in with an **access token** (not your password);
anonymous pulls are rate-limited.

## Visual

```text
 what you type            what Docker means
 nginx:1.30-alpine    ─▶  docker.io / library / nginx      : 1.30-alpine     official image
 bitnami/redis:8      ─▶  docker.io / bitnami / redis      : 8               a publisher's namespace
 alice/cafe-api:1.0   ─▶  docker.io / alice   / cafe-api   : 1.0             a user's repository

 push: docker login (user + access token) ──▶ docker push alice/cafe-api:1.0
 pull: anonymous (rate-limited per IP) or logged in (higher limit, private repositories)
```

## Lab setup

No files are needed. This lesson never logs in to Docker Hub: the commands that need an account are shown, not run.
Create a free account at <https://hub.docker.com> if you want to try them.

## Demonstration

A short name is a Docker Hub name. Both spellings are the same image:

<!-- test: contains=same image; output -->
```bash
short=$(docker image inspect alpine:3.23 --format '{{.Id}}')
full=$(docker image inspect docker.io/library/alpine:3.23 --format '{{.Id}}')
echo "alpine:3.23                    -> $short"
echo "docker.io/library/alpine:3.23  -> $full"
[ "$short" = "$full" ] && echo "same image"
```

```text
alpine:3.23                    -> sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
docker.io/library/alpine:3.23  -> sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
same image
```

Docker records where an image came from, with the digest of what it downloaded:

<!-- test: contains=nginx@sha256; output -->
```bash
docker image inspect nginx:1.30-alpine --format '{{index .RepoDigests 0}}'
```

```text
nginx@sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94
```

A **digest** pins the exact content: a tag can be moved to a new image, a digest cannot. You can run an image by its
digest (here it is already on your computer, so nothing is downloaded):

<!-- test: contains=nginx/1.30; output -->
```bash
digest=$(docker image inspect nginx:1.30-alpine --format '{{index .RepoDigests 0}}')
docker run --rm --entrypoint nginx "$digest" -v 2>&1
```

```text
nginx version: nginx/1.30.5
```

**Publishing your own image** (needs an account; replace `YOUR_USER`). Create an access token on Docker Hub (Account
settings → Personal access tokens, "Read & Write"), then:

<!-- test: skip -->
```bash
docker login -u YOUR_USER                 # paste the access token when asked for the password
docker tag cafe-api:1.0 YOUR_USER/cafe-api:1.0
docker push YOUR_USER/cafe-api:1.0
docker logout
```

In scripts, never type the token on the command line (it ends up in the shell history); pipe it in:
`echo "$DOCKERHUB_TOKEN" | docker login -u YOUR_USER --password-stdin`.

## Command breakdown

| Command | What it does |
|---|---|
| `docker login [-u USER]` | log in to Docker Hub (or `docker login REGISTRY` for another registry) |
| `--password-stdin` | read the token from standard input, for scripts and CI |
| `docker logout` | remove the stored credentials |
| `{{.RepoDigests}}` | the registry digests of a local image |
| `IMAGE@sha256:…` | refer to an image by digest instead of tag |

## Hands-on lab

**Instructions.** Find out whether this Docker client has stored Docker Hub credentials: look at the client
configuration file `~/.docker/config.json`.

**Expected result.** Either no file / no `auths` entry (never logged in), or an `auths` entry for
`https://index.docker.io/v1/`, usually with a `credsStore` (the credentials themselves are kept by the operating
system's credential store, not in the file).

**Verification.**

<!-- test: contains=logins -->
```bash
if grep -q '"auths"' ~/.docker/config.json 2> /dev/null && grep -q 'index.docker.io' ~/.docker/config.json; then
  echo "saved logins: Docker Hub"
else
  echo "saved logins: none for Docker Hub"
fi
```

## Break it

Try to publish without logging in:

<!-- test: fail; anyof=denied||unauthorized||authentication required||429 Too Many Requests; output -->
```bash
docker tag alpine:3.23 cafe-student/cafe-api:1.0
docker push cafe-student/cafe-api:1.0 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
```

## Troubleshoot it

`push access denied … may require authorization`: Docker Hub refuses anonymous pushes, and you can only push into a
namespace you own (your user name or an organisation you belong to). The message is the same whether the repository
does not exist or you lack permission: registries do not reveal which private repositories exist. Check the two
conditions:

<!-- test: contains=namespace; output -->
```bash
echo "namespace in the image name: $(echo cafe-student/cafe-api:1.0 | cut -d/ -f1)"
grep -q 'index.docker.io' ~/.docker/config.json 2> /dev/null && echo "logged in: yes" || echo "logged in: no"
```

```text
namespace in the image name: cafe-student
logged in: no
```

## Fix it

Log in as the owner of the namespace (with a token that allows writing), and name the image with your namespace:

<!-- test: skip -->
```bash
echo "$DOCKERHUB_TOKEN" | docker login -u YOUR_USER --password-stdin
docker tag alpine:3.23 YOUR_USER/cafe-api:1.0
docker push YOUR_USER/cafe-api:1.0
```

Remove the practice tag:

<!-- test -->
```bash
docker image rm cafe-student/cafe-api:1.0 > /dev/null
```

## Practice challenge

Show the difference between a tag and a digest: give the `nginx:1.29-alpine` image the tag `cafe/web:stable`, then
"release" `nginx:1.30-alpine` under the same tag. Print which nginx version `cafe/web:stable` runs before and after,
and which one the registry digest of `nginx:1.29-alpine` (noted before the release) runs.

<details>
<summary>Solution</summary>

<!-- test: contains=digest still runs nginx/1.29; output -->
```bash
docker tag nginx:1.29-alpine cafe/web:stable
pinned=$(docker image inspect nginx:1.29-alpine --format '{{range .RepoDigests}}{{println .}}{{end}}' | grep '^nginx@')
echo "stable before: $(docker run --rm --entrypoint nginx cafe/web:stable -v 2>&1)"
docker tag nginx:1.30-alpine cafe/web:stable
echo "stable after:  $(docker run --rm --entrypoint nginx cafe/web:stable -v 2>&1)"
echo "digest still runs $(docker run --rm --entrypoint nginx "$pinned" -v 2>&1 | cut -d' ' -f3)"
docker image rm cafe/web:stable > /dev/null
```

```text
stable before: nginx version: nginx/1.29.8
stable after:  nginx version: nginx/1.30.5
digest still runs nginx/1.29.8
```

A tag is a movable pointer, on Docker Hub as locally. (The digest is taken from `nginx@…`, the name it has on Docker
Hub: a digest is only useful together with a repository that holds that content.) Production deployments that must be reproducible pin by digest
(`nginx@sha256:…`), or at least by a full version tag, never by `latest` (lesson 021).

</details>

## Real-world example

A team hit `toomanyrequests` in CI: dozens of jobs pulled base images anonymously from Docker Hub through one shared
IP address. They now log in with an organisation's read-only token in CI, and mirror their base images into their own
registry (lesson 078), so builds no longer depend on Docker Hub's limits or availability. Their own images are pushed
with a token that can write only to their organisation's repositories.

## Recap

- A name without a registry is a Docker Hub name: `nginx` = `docker.io/library/nginx`.
- Log in with an access token (`--password-stdin` in scripts); push only to a namespace you own.
- Tags move, digests do not: pin by digest for reproducibility.
- Anonymous pulls are rate-limited: log in or mirror in CI.

## Cleanup

Nothing to clean: the practice tags were removed.

Next: [Lesson 077 · Image naming](../077-image-naming/README.md)
