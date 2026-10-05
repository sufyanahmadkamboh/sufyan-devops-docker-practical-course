# Module 19 assessment · Docker in CI/CD

> Lessons [135](135-docker-in-ci/README.md)–[137](137-scanning-and-testing-in-ci/README.md) · ⏱ 40 minutes · try every
> question before opening its answer

## Knowledge check

**1. Name the four steps of a Docker pipeline, in order, and what happens when one fails.**

<details><summary>Answer</summary>

Test, build, smoke test, push. A failing step stops the pipeline, so a broken image never reaches the registry
(lesson 135).

</details>

**2. Why do the tests run in their own Dockerfile stage?**

<details><summary>Answer</summary>

`docker build --target test` runs them inside the build with exactly the image's dependencies, and the production
stage, built from the same base, ships without the tests (lesson 135).

</details>

**3. Why tag images with the Git commit or a version instead of `latest`?**

<details><summary>Answer</summary>

An immutable tag always names the same image: you can tell which commit runs, deploy exactly what was tested, and roll
back to a previous tag. `latest` moves with every push (lessons 021, 135).

</details>

**4. How does a GitHub Actions job push to `ghcr.io` without a stored password?**

<details><summary>Answer</summary>

With the job's own `GITHUB_TOKEN`, which expires when the job ends, and `permissions: packages: write` in the
workflow (lesson 136).

</details>

**5. Why pin actions to a full commit SHA rather than `@v7`?**

<details><summary>Answer</summary>

A tag can be moved to different code (by mistake or by an attacker); a commit SHA cannot. The comment next to it keeps
the version readable (lesson 136).

</details>

**6. `docker push node-api:1.0` fails with `denied`. Why?**

<details><summary>Answer</summary>

Without a registry host the name means Docker Hub (`docker.io/library/node-api`), where you may not push. Tag the
image with its destination, e.g. `ghcr.io/OWNER/node-api:1.0` (lesson 136).

</details>

**7. Name four rules a policy gate can check with `docker image inspect` alone.**

<details><summary>Answer</summary>

A version tag, a non-root user, a healthcheck, no secret-like environment variables, a size budget (lesson 137).

</details>

**8. What does a vulnerability scanner check that a policy gate does not?**

<details><summary>Answer</summary>

The packages and libraries inside the image against databases of known vulnerabilities (CVEs), for example with
Trivy or Docker Scout (lesson 137).

</details>

## Practical task

Run the complete pipeline of lesson 135 for version `2.0.0` against a local registry, then prove that the pushed image
passes the policy gate of lesson 137.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-19 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/test ~/docker-practice/assessment-19/
cp 19-ci-cd/137-scanning-and-testing-in-ci/examples/Dockerfile 19-ci-cd/137-scanning-and-testing-in-ci/examples/image-policy.sh 19-ci-cd/135-docker-in-ci/examples/ci.sh ~/docker-practice/assessment-19/
cd ~/docker-practice/assessment-19
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
```

<!-- test: retry=3; contains=pipeline passed; contains=PASS  healthcheck; output -->
```bash
cd ~/docker-practice/assessment-19
VERSION=2.0.0 bash ci.sh
bash image-policy.sh localhost:5000/node-api:2.0.0
```

```text
== 1/4 test
== 2/4 build localhost:5000/node-api:2.0.0
== 3/4 smoke test
== 4/4 push
localhost:5000/node-api:2.0.0
pipeline passed: localhost:5000/node-api:2.0.0
PASS  version tag
PASS  non-root user
PASS  healthcheck
PASS  no secrets in ENV
PASS  size (59 MB, budget 300 MB)
```

The Dockerfile of lesson 137 is used because its production stage has the healthcheck the gate requires.

</details>

## Troubleshooting task

A colleague adds a configuration value to the image and the gate now fails:

<!-- test: fail; contains=FAIL  no secrets in ENV -->
```bash
cd ~/docker-practice/assessment-19
printf 'FROM localhost:5000/node-api:2.0.0\nENV PAYMENT_API_TOKEN=example-token-change-me\n' > Dockerfile.token
docker build -q -f Dockerfile.token -t node-api:2.0.1 . > /dev/null
bash image-policy.sh node-api:2.0.1
```

Explain the failure, show where the value is visible, and fix the image.

<details><summary>Solution</summary>

The gate found a secret-like variable baked into the image. Anyone who can pull the image reads it:

<!-- test: contains=PAYMENT_API_TOKEN=example-token-change-me -->
```bash
docker image inspect node-api:2.0.1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep TOKEN
```

The fix is to remove it from the image and give it to the container at run time, as a secret file (lesson 133):

<!-- test: contains=PASS  no secrets in ENV -->
```bash
cd ~/docker-practice/assessment-19
printf 'FROM localhost:5000/node-api:2.0.0\n' > Dockerfile.token
docker build -q -f Dockerfile.token -t node-api:2.0.1 . > /dev/null
bash image-policy.sh node-api:2.0.1
```

At run time: `-v "$(pwd)/secrets/payment_api_token:/run/secrets/payment_api_token:ro"`, read by the application.

</details>

## Real-world scenario

A team's pipeline builds on every push to `main`, tags the image `latest`, pushes it, and the servers pull `latest`
every night. Last week a broken commit was deployed and nobody could say which version had worked before. What would
you change?

<details><summary>Model answer</summary>

Run the tests in the build (test stage) and a smoke test before pushing, so broken commits never get pushed (lesson
135). Tag every image with the commit SHA (and releases with their version) and deploy those tags, never `latest`
(lesson 136): the deployed version is then always known, and a rollback is redeploying the previous tag. Add a policy
gate and a vulnerability scan before the push (lesson 137), and make the registry reject overwriting existing tags.

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f registry smoke > /dev/null 2>&1 || true
docker image rm -f node-api:test node-api:2.0.1 localhost:5000/node-api:2.0.0 > /dev/null
rm -rf ~/docker-practice/assessment-19
```
