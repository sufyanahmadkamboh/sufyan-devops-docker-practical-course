# Lesson 079 · GitHub Container Registry

> Level 12 · Registries · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

GitHub Container Registry (GHCR, `ghcr.io`) stores images next to the code: `ghcr.io/OWNER/IMAGE:TAG`, where `OWNER`
is a GitHub user or organisation. Access follows GitHub's permissions. From your computer you log in with a personal
access token that has the `write:packages` scope; in GitHub Actions the job's built-in `GITHUB_TOKEN` is enough, once
the workflow grants it `packages: write`. A label in the image links the package to its repository.

## Visual

```text
 your computer                                           GitHub
 docker login ghcr.io -u USER  (token: write:packages)   ┌───────────────────────────────────────────┐
 docker push ghcr.io/cafe-team/cafe-api:1.0  ──────────▶ │ Packages: cafe-team/cafe-api              │
                                                         │   tags 1.0, 1.1 …   visibility: private    │
 GitHub Actions workflow                                 │   connected repository (from the label    │
 permissions: packages: write                            │   org.opencontainers.image.source)        │
 GITHUB_TOKEN ──── docker login / push ────────────────▶ │                                           │
                                                         └───────────────────────────────────────────┘
 token scopes:  read:packages (pull)  write:packages (push, implies read)  delete:packages
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-079 11-registry/079-github-container-registry/examples
cd ~/docker-practice/lesson-079
cat Dockerfile
```

`cafe-team-example` stands for your GitHub user or organisation in this lesson.

## Demonstration

Build the image with its GHCR name. The name must be lowercase, even if your GitHub name has capitals:

<!-- test: contains=ghcr.io/cafe-team-example/cafe-api; output -->
```bash
docker build -q -t ghcr.io/cafe-team-example/cafe-api:1.0 . > /dev/null
docker image ls ghcr.io/cafe-team-example/cafe-api --format '{{.Repository}}:{{.Tag}}'
docker run --rm ghcr.io/cafe-team-example/cafe-api:1.0
```

```text
ghcr.io/cafe-team-example/cafe-api:1.0
cafe-api 1.0
```

The OCI labels are part of the image; GHCR reads `org.opencontainers.image.source` to connect the package to the
repository (and to give the repository's members access):

<!-- test: contains=github.com/cafe-team-example/cafe-api; output -->
```bash
docker image inspect ghcr.io/cafe-team-example/cafe-api:1.0 --format '{{range $k, $v := .Config.Labels}}{{$k}}={{$v}}{{"\n"}}{{end}}'
```

```text
org.opencontainers.image.description=Cafe API practice image
org.opencontainers.image.licenses=MIT
org.opencontainers.image.source=https://github.com/cafe-team-example/cafe-api
```

**Logging in from your computer** (needs a GitHub account). Either create a classic personal access token with the
`write:packages` scope (Settings → Developer settings → Personal access tokens), or let the GitHub CLI add the scope to
its own token:

<!-- test: skip -->
```bash
gh auth refresh -s write:packages           # once: adds the scope (opens the browser)
gh auth token | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
docker tag ghcr.io/cafe-team-example/cafe-api:1.0 ghcr.io/YOUR_GITHUB_USER/cafe-api:1.0
docker push ghcr.io/YOUR_GITHUB_USER/cafe-api:1.0
```

A new package is **private**; change its visibility in the package's settings on GitHub to let anyone pull it.

**From GitHub Actions**, no personal token is needed (`docker-publish.yml` in the lab folder):

<!-- test: contains=packages: write; output -->
```bash
grep -E "permissions|packages|GITHUB_TOKEN|docker (push|build)" docker-publish.yml
```

```text
    permissions:
      packages: write          # lets GITHUB_TOKEN push to ghcr.io/OWNER/*
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
          docker build -t "$image" .
          docker push "$image"
```

`${GITHUB_REPOSITORY_OWNER,,}` lowercases the owner (bash), because image names must be lowercase. The CI/CD module
(lesson 136) builds and pushes this way.

## Command breakdown

| Item | Meaning |
|---|---|
| `ghcr.io/OWNER/IMAGE:TAG` | the GHCR name; `OWNER` = user or organisation, lowercase |
| `write:packages` / `read:packages` / `delete:packages` | token scopes for pushing / pulling / deleting |
| `gh auth refresh -s write:packages` | add the scope to the GitHub CLI's token |
| `permissions: packages: write` | lets a workflow's `GITHUB_TOKEN` push packages |
| `LABEL org.opencontainers.image.source=URL` | connect the package to a repository |

## Hands-on lab

**Instructions.** Add the label `org.opencontainers.image.version` with the value `1.0` at build time, without editing
the Dockerfile (`docker build --label`), and read it back.

**Expected result.** `1.0`.

**Verification.**

<!-- test: contains=1.0 -->
```bash
cd ~/docker-practice/lesson-079
docker build -q --label org.opencontainers.image.version=1.0 -t ghcr.io/cafe-team-example/cafe-api:1.0 . > /dev/null
docker image inspect ghcr.io/cafe-team-example/cafe-api:1.0 --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
```

## Break it

Push without logging in:

<!-- test: fail; anyof=unauthorized||denied||authentication required; output -->
```bash
docker push ghcr.io/cafe-team-example/cafe-api:1.0 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
denied
```

## Troubleshoot it

GHCR refuses anonymous pushes. With a login, three more causes give similar messages:

| Message after `docker login ghcr.io` | Cause | Fix |
|---|---|---|
| `denied: permission_denied: The token provided does not match expected scopes` | token without `write:packages` | new token, or `gh auth refresh -s write:packages` |
| `denied: permission_denied: write_package` | the owner in the name is not you or your organisation, or the workflow lacks `packages: write` | correct the name / add the permission |
| `denied: installation not allowed to Write organization package` | the package exists and is not connected to this repository | in the package settings, give the repository write access |

Check what this client has stored for ghcr.io, and which scopes the GitHub CLI's token has:

<!-- test: contains=ghcr.io; output -->
```bash
grep -q '"ghcr.io"' ~/.docker/config.json 2> /dev/null && echo "ghcr.io login stored: yes" || echo "ghcr.io login stored: no"
```

```text
ghcr.io login stored: no
```

<!-- test: skip -->
```bash
gh auth status          # lists "Token scopes: … write:packages …" when the scope is there
```

## Fix it

Log in with a token that has `write:packages`, and push to your own namespace:

<!-- test: skip -->
```bash
gh auth token | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
docker tag ghcr.io/cafe-team-example/cafe-api:1.0 ghcr.io/your_github_user/cafe-api:1.0
docker push ghcr.io/your_github_user/cafe-api:1.0
```

## Practice challenge

Write the image name a workflow should use for a repository owned by `Cafe-Team` (capital letters) and the Git tag
`v2.3.0`, the way `docker-publish.yml` computes it, and check that Docker accepts it.

<details>
<summary>Solution</summary>

<!-- test: contains=ghcr.io/cafe-team/cafe-api:2.3.0; output -->
```bash
GITHUB_REPOSITORY_OWNER=Cafe-Team GITHUB_REF_NAME=v2.3.0 bash -c '
  image=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/cafe-api:${GITHUB_REF_NAME#v}
  echo "$image"
  docker tag ghcr.io/cafe-team-example/cafe-api:1.0 "$image" && echo "valid name"
  docker image rm "$image" > /dev/null'
```

```text
ghcr.io/cafe-team/cafe-api:2.3.0
valid name
```

`${VAR,,}` lowercases, `${VAR#v}` removes the leading `v`: `v2.3.0` becomes the tag `2.3.0`. (`${VAR,,}` needs bash 4
or newer: GitHub's runners, Linux and Git Bash have it; macOS's built-in bash 3.2 does not, use
`echo "$VAR" | tr '[:upper:]' '[:lower:]'` there.)

</details>

## Real-world example

An open-source project publishes its images on GHCR from a release workflow: the Git tag `v2.3.0` becomes
`ghcr.io/project/app:2.3.0`, pushed with `GITHUB_TOKEN`, so no maintainer's personal token is stored anywhere. The
package is public and connected to the repository, so its page shows the README and the source, and only the
repository's maintainers can push.

## Recap

- GHCR names: `ghcr.io/owner/image:tag`, lowercase.
- From your computer: a token with `write:packages` (`gh auth refresh -s write:packages`), `--password-stdin`.
- From Actions: `GITHUB_TOKEN` with `permissions: packages: write`.
- `org.opencontainers.image.source` connects the package to its repository; new packages are private.

## Cleanup

<!-- test -->
```bash
docker image rm ghcr.io/cafe-team-example/cafe-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-079
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 080 · The attack surface of a container](../../12-security/080-attack-surface/README.md)
