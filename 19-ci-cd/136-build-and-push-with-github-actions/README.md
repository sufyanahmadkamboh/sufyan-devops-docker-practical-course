# Lesson 136 · Build and push with GitHub Actions

> Level 20 · Docker in CI/CD · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

How the pipeline of lesson 135 looks in a real CI system: a GitHub Actions workflow that tests and builds the image on
every pull request, and pushes it to the **GitHub Container Registry** (`ghcr.io`) on every push to `main` and every
version tag. The workflow logs in with the job's own short-lived `GITHUB_TOKEN`, so no password is stored anywhere.
This lesson keeps the GitHub Actions details to what Docker needs; the workflow syntax itself belongs to a CI course.

## Visual

```text
 .github/workflows/docker-image.yml

 pull request ──▶ checkout ─▶ buildx ─▶ build --target test ─▶ build --target production       (no push)
 push to main ──▶    〃         〃              〃                 + login ghcr.io ─▶ push
 tag v1.4.0   ──▶    〃         〃              〃                 + login ghcr.io ─▶ push

 tags written (docker/metadata-action):
   ghcr.io/OWNER/node-api:sha-3f9c2a1e…    every push: the exact commit
   ghcr.io/OWNER/node-api:main             the branch (moves with each push)
   ghcr.io/OWNER/node-api:1.4.0            a release tag v1.4.0 (never moves)

 GITHUB_TOKEN + "permissions: packages: write"  =  the job may push to ghcr.io/OWNER/*
```

| Workflow step | Same as in `ci.sh` (lesson 135) |
|---|---|
| `docker/build-push-action` with `target: test` | `docker build --target test .` |
| `docker/metadata-action` | choosing the tags (`VERSION`) |
| `docker/login-action` with `GITHUB_TOKEN` | `docker login ghcr.io` |
| `docker/build-push-action` with `target: production`, `push: true` | `docker build --target production -t … && docker push …` |
| `cache-from/cache-to: type=gha` | the local build cache, stored between CI runs |

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-136 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/. ~/docker-practice/lesson-136/
mkdir -p ~/docker-practice/lesson-136/.github/workflows
cp 19-ci-cd/136-build-and-push-with-github-actions/examples/docker-image.yml ~/docker-practice/lesson-136/.github/workflows/
cd ~/docker-practice/lesson-136
git init -q -b main && git add -A && git -c user.name="Course Learner" -c user.email="learner@example.com" commit -qm "node-api with CI"
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
git log --oneline
```

The project of lesson 135 as a Git repository, with the workflow in `.github/workflows/`, and a local registry
standing in for `ghcr.io`.

## Demonstration

The workflow's actions, each pinned to a full commit SHA (a tag like `v7` could be moved to different code):

<!-- test: contains=docker/build-push-action@; output -->
```bash
grep -E 'uses:|permissions|packages|target:|push:' .github/workflows/docker-image.yml
```

```text
  push:
permissions:
  packages: write          # push to ghcr.io with the job's own GITHUB_TOKEN
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1          # v7.0.1
      - uses: docker/setup-buildx-action@f87e5991a6d7451dcb8d9637bfbc97413f497069 # v4.4.1
        uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc  # v7.4.0
          target: test
          push: false
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302    # v6.2.0
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f       # v4.6.0
      # 2 build and 4 push: pull requests build but never push
        uses: docker/build-push-action@c3c9e263c25d99ce0380d002d59b67737d91b0dc  # v7.4.0
          target: production
          push: ${{ github.event_name != 'pull_request' }}
```

Run the steps a push to `main` triggers, locally, with the tags the metadata step would compute:

<!-- test: retry=3; contains=sha-; output -->
```bash
sha=$(git rev-parse HEAD)
image=localhost:5000/node-api
docker build -q --target test . > /dev/null && echo "test stage: passed"
docker build -q --target production -t "$image:sha-$sha" -t "$image:main" . > /dev/null
docker push -q "$image:sha-$sha" > /dev/null
docker push -q "$image:main" > /dev/null
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

```text
test stage: passed
{"name":"node-api","tags":["main","sha-03a1a1a3b2d049a068bdf7d764c9032f13deb55d"]}
```

In GitHub, the same happens on `ubuntu-24.04` runners, and the result appears under the repository's **Packages**.

## Command breakdown

| Workflow element | What it does |
|---|---|
| `on: push / pull_request` | when the workflow runs; pull requests build and test but never push |
| `permissions: packages: write` | allows the job's `GITHUB_TOKEN` to push packages (images) |
| `docker/login-action` + `secrets.GITHUB_TOKEN` | log in to `ghcr.io` with a token valid only for this job |
| `images: ghcr.io/${{ github.repository_owner }}/node-api` | the image name: registry host / owner / name |
| `type=sha,format=long` | tag `sha-<full commit SHA>` |
| `push: ${{ github.event_name != 'pull_request' }}` | push only for pushes and tags |

On your own GitHub repository, the push is the only manual step: commit this folder, push, and watch the
**Actions** tab:

<!-- test: skip -->
```bash
git remote add origin https://github.com/YOUR-USER/node-api.git
git push -u origin main
gh run watch                      # follow the workflow (GitHub CLI)
docker pull ghcr.io/YOUR-USER/node-api:main
```

## Hands-on lab

**Instructions.** Release version 1.0.0: create the Git tag `v1.0.0`, and push the image tag the metadata step derives
from it (`1.0.0`, without the `v`) to the local registry.

**Expected result.** The registry lists `1.0.0`, `main` and `sha-…`.

**Verification.**

<!-- test: contains="1.0.0" -->
```bash
cd ~/docker-practice/lesson-136
git tag v1.0.0
version=$(git describe --tags --exact-match | sed 's/^v//')
docker tag localhost:5000/node-api:main "localhost:5000/node-api:$version"
docker push -q "localhost:5000/node-api:$version" > /dev/null
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

## Break it

A new team member builds the image as `node-api:main` (no registry in the name) and pushes it:

<!-- test: fail; anyof=denied||unauthorized||insufficient_scope||429 Too Many Requests||toomanyrequests; output -->
```bash
cd ~/docker-practice/lesson-136
docker tag localhost:5000/node-api:main node-api:main
docker push node-api:main 2>&1 | grep -v Waiting
test "${PIPESTATUS[0]}" -eq 0
```

```text
The push refers to repository [docker.io/library/node-api]
push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
```

(`grep -v Waiting` only hides the progress lines of the layers.)

## Troubleshoot it

The first line of the push output names the repository Docker used: `docker.io/library/node-api`. An image name
without a registry host means Docker Hub, and `library/` is reserved for Docker's official images, so the push is
refused (or, with too many anonymous requests, rate-limited). The name decides the destination (lesson 077):

| Name | Pushed to |
|---|---|
| `node-api:main` | `docker.io/library/node-api` (Docker Hub, official images: refused) |
| `localhost:5000/node-api:main` | the registry on `localhost:5000` |
| `ghcr.io/OWNER/node-api:main` | GitHub Container Registry, owner `OWNER` |

The same mistake in the workflow looks different: pushing to `ghcr.io` without `permissions: packages: write` fails
with `denied: installation not allowed to Create organization package` or `permission_denied: write_package`. Both
mean the same thing: the token may read, not write.

## Fix it

Name the image after its destination, as the metadata step does with `images: ghcr.io/…`:

<!-- test: contains=pushed -->
```bash
cd ~/docker-practice/lesson-136
docker tag node-api:main localhost:5000/node-api:main
docker push -q localhost:5000/node-api:main > /dev/null && echo "pushed localhost:5000/node-api:main"
```

## Practice challenge

Pull requests must never push. Show, from the workflow file, which expression prevents it, and which step is skipped
entirely for pull requests.

<details>
<summary>Solution</summary>

<!-- test: contains=pull_request; output -->
```bash
cd ~/docker-practice/lesson-136
grep -n "pull_request" .github/workflows/docker-image.yml
```

```text
9:  pull_request:
41:        if: github.event_name != 'pull_request'
52:          push: ${{ github.event_name != 'pull_request' }}
```

The login step has `if: github.event_name != 'pull_request'` (it is skipped), and the build step pushes only when
`push:` evaluates to `true`, which is false for pull requests. Pull requests from forks also get a read-only token,
so even a modified workflow could not push.

</details>

## Real-world example

A team's repositories all contain the same short workflow. Every pull request proves the image builds and its tests
pass; every merge to `main` publishes `sha-<commit>` and `main`; every release tag publishes the version. Deployments
reference `sha-` or version tags only, and because `GITHUB_TOKEN` expires when the job ends, there is no registry
password to rotate or leak.

## Recap

- GitHub Actions runs the same Docker steps as a local script: test stage, build, login, push.
- `GITHUB_TOKEN` with `permissions: packages: write` pushes to `ghcr.io/OWNER/...`; no stored password.
- Pin actions to commit SHAs; tag images with the commit, the branch and the release version.
- The image name chooses the registry: no host means Docker Hub.

## Cleanup

<!-- test -->
```bash
docker rm -f registry > /dev/null
docker image rm -f node-api:main $(docker image ls -q localhost:5000/node-api | sort -u) > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-136
```

Next: [Lesson 137 · Scanning and testing in CI](../137-scanning-and-testing-in-ci/README.md)
