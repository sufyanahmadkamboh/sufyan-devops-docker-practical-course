# Lesson 137 · Scanning and testing in CI

> Level 20 · Docker in CI/CD · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

Unit tests prove the code works. Before an image is pushed, a pipeline should also prove the **image** is acceptable:
it starts and answers (**smoke test**), it follows the team's rules (**policy gate**: non-root, healthcheck, no
secrets, a size budget, a version tag), and it has no known serious vulnerabilities (**vulnerability scan**). Each gate
is a command that exits non-zero when the image fails it, so the pipeline stops before the push.

## Visual

```text
 build ──▶ unit tests ──▶ smoke test ──▶ policy gate ──────────────▶ vulnerability scan ──▶ push
           (test stage)   (it starts,    image-policy.sh:              trivy / docker scout
                          /health = ok)  version tag · non-root ·      known CVEs in OS packages
                                         healthcheck · no ENV secrets  and libraries, HIGH/CRITICAL
                                         · size budget                 with a fix → fail
              exit ≠ 0 at any gate ──▶ pipeline stops, nothing pushed
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-137 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/test ~/docker-practice/lesson-137/
cp 19-ci-cd/137-scanning-and-testing-in-ci/examples/* ~/docker-practice/lesson-137/
cd ~/docker-practice/lesson-137
docker build -q --target production -t node-api:1.0.0 . > /dev/null
ls
```

The API with the three-stage Dockerfile of lesson 135 (now with a `HEALTHCHECK` in its production stage), the policy
gate `image-policy.sh` and a scan step for the workflow of lesson 136.

## Demonstration

Run the policy gate against the production image:

<!-- test: contains=PASS  non-root user; output -->
```bash
bash image-policy.sh node-api:1.0.0
echo "exit code: $?"
```

```text
PASS  version tag
PASS  non-root user
PASS  healthcheck
PASS  no secrets in ENV
PASS  size (59 MB, budget 300 MB)
exit code: 0
```

Every rule is one `docker image inspect` query (read the script: it is 50 lines). The smoke test from lesson 135
checks behavior; with a `HEALTHCHECK` in the image it becomes a single wait for the health status:

<!-- test: retry=15; contains=healthy; output -->
```bash
docker run -d --name smoke node-api:1.0.0 > /dev/null 2>&1 || true
docker inspect smoke --format '{{.State.Health.Status}}'
```

```text
healthy
```

**Vulnerability scanning.** Scanners compare the packages inside the image (Alpine packages, npm modules, Go
modules, …) with databases of known vulnerabilities. The two most common:

<!-- test: skip -->
```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 node-api:1.0.0
docker scout cves --only-severity critical,high --exit-code node-api:1.0.0
```

This course does not run them in its tests: Trivy downloads its database (hundreds of MB) on every run, and Docker
Scout needs a Docker Hub account. In GitHub Actions, add [scan-step.yml](examples/scan-step.yml) to the workflow of
lesson 136: the scan fails the job when a HIGH or CRITICAL vulnerability with an available fix is found.

## Command breakdown

| Gate | Command | Fails when |
|---|---|---|
| unit tests | `docker build --target test` | a test fails |
| smoke test | `docker run -d` + `docker inspect --format '{{.State.Health.Status}}'` | not `healthy` in time |
| policy | `bash image-policy.sh IMAGE` | root, no healthcheck, secret-like ENV, too big, `latest` |
| vulnerabilities | `trivy image --exit-code 1 IMAGE` | known HIGH/CRITICAL vulnerabilities with a fix |

## Hands-on lab

**Instructions.** Use the gate the way a pipeline does: push to the local registry only if the gate passes.

**Expected result.** All five rules pass, then `push allowed`.

**Verification.**

<!-- test: contains=push allowed -->
```bash
cd ~/docker-practice/lesson-137
bash image-policy.sh node-api:1.0.0 && echo "push allowed"
```

## Break it

A change to the pipeline builds the wrong stage: `--target base` instead of `--target production`. The image works
perfectly:

<!-- test: fail; contains=FAIL  non-root user; output -->
```bash
cd ~/docker-practice/lesson-137
docker build -q --target base -t node-api:1.0.1 . > /dev/null
docker run --rm node-api:1.0.1 node -e "console.log('it runs')"
bash image-policy.sh node-api:1.0.1
```

```text
it runs
PASS  version tag
FAIL  non-root user: runs as root (set USER)
FAIL  healthcheck: no HEALTHCHECK
PASS  no secrets in ENV
PASS  size (59 MB, budget 300 MB)
```

## Troubleshoot it

The gate names the failing rules: no user, no healthcheck. Both are set only in the `production` stage, so the image
was built from another stage. Confirm with the image's configuration and the Dockerfile's stages:

<!-- test: contains=AS production; output -->
```bash
cd ~/docker-practice/lesson-137
docker image inspect node-api:1.0.1 --format 'user="{{.Config.User}}" healthcheck={{.Config.Healthcheck}}'
grep -n "^FROM" Dockerfile
```

```text
user="" healthcheck=<nil>
2:FROM node:24-alpine AS base
10:FROM base AS test
15:FROM base AS production
```

`base` has the code and dependencies but no `USER` and no `HEALTHCHECK`: a root image that nobody can monitor would
have been pushed if the gate had not stopped it. A test that only runs the application would never notice.

## Fix it

<!-- test: contains=PASS  healthcheck -->
```bash
cd ~/docker-practice/lesson-137
docker build -q --target production -t node-api:1.0.1 . > /dev/null
bash image-policy.sh node-api:1.0.1
```

## Practice challenge

Your team decides on a size budget of 10 MB for this image (impossible with Node.js, which is the point). Run the gate
with that budget, and show that only the size rule fails.

<details>
<summary>Solution</summary>

<!-- test: contains=FAIL  size; output -->
```bash
cd ~/docker-practice/lesson-137
MAX_MB=10 bash image-policy.sh node-api:1.0.1 || echo "gate failed: exit code $?"
```

```text
PASS  version tag
PASS  non-root user
PASS  healthcheck
PASS  no secrets in ENV
FAIL  size (59 MB, budget 10 MB): 59 MB > 10 MB
gate failed: exit code 1
```

A budget turns "the image got bigger" into a visible, reviewable decision. To meet a small budget, the image must
change (a smaller base, multi-stage builds: module 13), or the team raises the budget on purpose.

</details>

## Real-world example

A platform team publishes one policy for all images: non-root, healthcheck, no secrets, signed, scanned. Each
service's pipeline runs the same gates before pushing, and the cluster's admission controller rejects images that
were not signed by the pipeline, so an image built and pushed by hand cannot be deployed at all. When a new critical
vulnerability is published, the weekly scheduled scan of all images in the registry shows which services must be
rebuilt.

## Recap

- Gate the image, not only the code: smoke test, policy, vulnerability scan.
- Each gate is a command with a non-zero exit code on failure, so the pipeline stops before the push.
- A policy gate is a few `docker image inspect` queries: user, healthcheck, environment, size, tag.
- Scanners (Trivy, Docker Scout) find known vulnerabilities in OS packages and libraries; run them in CI.

## Cleanup

<!-- test -->
```bash
docker rm -f smoke > /dev/null
docker image rm -f node-api:1.0.0 node-api:1.0.1 > /dev/null
rm -rf ~/docker-practice/lesson-137
```

Next: [Lesson 138 · From Docker to Kubernetes](../../20-kubernetes/138-from-docker-to-kubernetes/README.md)
