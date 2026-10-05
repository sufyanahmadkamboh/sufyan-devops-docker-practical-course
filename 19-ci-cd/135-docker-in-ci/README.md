# Lesson 135 · Docker in CI

> Level 20 · Docker in CI/CD · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

In a team, nobody builds production images on a laptop. A **CI pipeline** does it on every change, always the same
way: **test** the code, **build** the image, **smoke-test** the container, and only then **push** it to a registry with
an **immutable tag** (the version or the Git commit). If any step fails, nothing is pushed. This lesson runs exactly
those steps with a small script you can read in a minute; lesson 136 runs the same steps in GitHub Actions.

## Visual

```text
  git push
     │
     ▼
 ┌────────────┐    ┌────────────┐    ┌──────────────┐    ┌───────────────────────────┐
 │ 1 test     │──▶ │ 2 build    │──▶ │ 3 smoke test │──▶ │ 4 push                    │──▶ deploy (lesson 139)
 │ build the  │    │ production │    │ run it, ask  │    │ registry/node-api:1.0.0   │
 │ test stage │    │ stage, tag │    │ /health      │    │ (never overwritten)       │
 └─────┬──────┘    └─────┬──────┘    └──────┬───────┘    └───────────────────────────┘
       └── any failure stops the pipeline: a broken image never reaches the registry
```

One Dockerfile, three stages: `base` (dependencies and code), `test` (`base` + the tests, which run during the build)
and `production` (`base` + a non-root user). The tests never ship.

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-135 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/. ~/docker-practice/lesson-135/
cd ~/docker-practice/lesson-135
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
ls
```

The API, its tests (`test/server.test.js`), the three-stage `Dockerfile`, the pipeline `ci.sh`, and a local registry
on port 5000 in place of Docker Hub or GHCR.

## Demonstration

Read the pipeline first: it is four commands and a loop.

<!-- test: contains=docker push; output -->
```bash
grep -E '^echo "==|docker (build|run|push)' ci.sh
```

```text
echo "== 1/4 test"
docker build -q --target test -t node-api:test . > /dev/null
echo "== 2/4 build $image"
docker build -q --target production -t "$image" . > /dev/null
echo "== 3/4 smoke test"
docker run -d --name smoke "$image" > /dev/null
echo "== 4/4 push"
docker push -q "$image"
```

Run it for version `1.0.0`:

<!-- test: retry=3; contains=pipeline passed; output -->
```bash
VERSION=1.0.0 bash ci.sh
```

```text
== 1/4 test
== 2/4 build localhost:5000/node-api:1.0.0
== 3/4 smoke test
== 4/4 push
localhost:5000/node-api:1.0.0
pipeline passed: localhost:5000/node-api:1.0.0
```

The registry now has the version:

<!-- test: contains="1.0.0"; output -->
```bash
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

```text
{"name":"node-api","tags":["1.0.0"]}
```

## Command breakdown

| Command | Pipeline step |
|---|---|
| `docker build --target test` | build up to the `test` stage: its `RUN node --test` runs the tests |
| `docker build --target production -t REGISTRY/node-api:VERSION` | the image that ships, tagged with its version |
| `docker run -d` + `docker exec … /health` | the smoke test: does the container start and answer? |
| `docker push` | publish; reached only if every earlier step passed (`set -e`) |
| `curl …/v2/node-api/tags/list` | the registry's API: which tags exist (lesson 078) |

## Hands-on lab

**Instructions.** Show that the shipped image contains no tests and does not run as root, and that the tests exist
only in the test stage.

**Expected result.** `ls /app` in the production image shows no `test` folder; the user is `node`.

**Verification.**

<!-- test: contains=user=node; absent=test -->
```bash
docker run --rm localhost:5000/node-api:1.0.0 ls /app
echo "user=$(docker image inspect localhost:5000/node-api:1.0.0 --format '{{.Config.User}}')"
```

## Break it

A teammate changes the greeting and pushes without running the tests:

<!-- test: fail; contains=1/4 test; output=tail:6 -->
```bash
cd ~/docker-practice/lesson-135
sed 's|Hello from Node.js|Hi from Node.js|' server.js > server.new && mv server.new server.js
VERSION=1.1.0 bash ci.sh 2>&1
```

```text
...
  13 |     
  14 |     # the image that is shipped: no tests, no root
--------------------
ERROR: failed to build: failed to solve: process "/bin/sh -c node --test" did not complete successfully: exit code: 1

View build details: docker-desktop://dashboard/build/default/default/gkkylrqte2d17p5g0i699zawx
```

## Troubleshoot it

The pipeline stopped at step 1: the `RUN node --test` step of the test stage failed, so `docker build` failed and
`set -e` ended the script. Nothing was pushed:

<!-- test: absent=1.1.0; output -->
```bash
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

```text
{"name":"node-api","tags":["1.0.0"]}
```

To see the full test report, run the test stage alone with plain progress output, and look for the failing test:

<!-- test: fail; contains=Hi from Node.js -->
```bash
cd ~/docker-practice/lesson-135
docker build --target test --progress=plain . 2>&1 | grep -E "not ok|expected|actual" | head -5
test "${PIPESTATUS[0]}" -eq 0
```

The test expected `Hello from Node.js` and got `Hi from Node.js`: the change broke the API's contract.

## Fix it

Either the change is wrong (revert it), or the contract really changes (update the test in the same commit). Here
the change was a mistake:

<!-- test: retry=3; contains=pipeline passed -->
```bash
cd ~/docker-practice/lesson-135
sed 's|Hi from Node.js|Hello from Node.js|' server.js > server.new && mv server.new server.js
VERSION=1.1.0 bash ci.sh
```

## Practice challenge

Tags in a registry should be **immutable**: version `1.0.0` must always mean the same image. Show that the image
pushed as `1.0.0` and the one pushed as `1.1.0` have different digests, and pull `1.0.0` back by its digest.

<details>
<summary>Solution</summary>

<!-- test: contains=pulled by digest; output -->
```bash
for v in 1.0.0 1.1.0; do
  docker image inspect localhost:5000/node-api:$v --format "$v {{index .RepoDigests 0}}"
done
digest=$(docker image inspect localhost:5000/node-api:1.0.0 --format '{{index .RepoDigests 0}}')
docker pull -q "$digest" > /dev/null && echo "pulled by digest: $digest"
```

```text
1.0.0 localhost:5000/node-api@sha256:a9f4b0681564b2991fbe68d8d03e00115ceee9e696a8ffb3bb9ec767c9c0d604
1.1.0 localhost:5000/node-api@sha256:bc87e0b193685bb7df5116ddd0038d41bc38761a4cac748fee180e7fd742abaa
pulled by digest: localhost:5000/node-api@sha256:a9f4b0681564b2991fbe68d8d03e00115ceee9e696a8ffb3bb9ec767c9c0d604
```

The two versions have different digests even though their code is identical: each build writes new image metadata
(its creation time, for example), and the digest covers the metadata too. A deployment that names the digest gets exactly the image that passed the pipeline, even if someone
later pushed a different image under the same tag.

</details>

## Real-world example

A team's pipeline tags every image with the Git commit (`node-api:3f9c2a1`) and, for releases, with the version
(`node-api:1.4.0`). Deployments always reference one of those tags, never `latest`, so the cluster can always answer
"which commit is running?" and a rollback is deploying the previous tag. The registry is configured to reject
overwriting an existing tag (ECR "tag immutability", for example).

## Recap

- A Docker pipeline: test → build → smoke test → push, and a failing step stops everything.
- A multi-stage Dockerfile gives the tests their own stage; the shipped image contains no tests.
- Tag with immutable versions (version, commit); deploy by tag or, even safer, by digest.
- The same steps run on a laptop (`ci.sh`) and in CI (lesson 136).

## Cleanup

<!-- test -->
```bash
docker rm -f registry smoke > /dev/null 2>&1 || true
docker image rm -f node-api:test localhost:5000/node-api:1.0.0 localhost:5000/node-api:1.1.0 > /dev/null
rm -rf ~/docker-practice/lesson-135
```

Next: [Lesson 136 · Build and push with GitHub Actions](../136-build-and-push-with-github-actions/README.md)
