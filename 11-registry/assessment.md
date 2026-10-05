# Module 11 assessment · Registries

> Lessons [075](075-what-is-a-registry/README.md)–[079](079-github-container-registry/README.md) · ⏱ 30 minutes ·
> try every question before opening its answer

## Knowledge check

**1. Which registry, repository and tag does `postgres` refer to?**

<details><summary>Answer</summary>

`docker.io/library/postgres:latest`: Docker Hub, the official image's repository `library/postgres`, tag `latest`
(lessons 076, 077).

</details>

**2. You run `docker push cafe-api:1.0`. Where does Docker try to send it, and why does it fail?**

<details><summary>Answer</summary>

To Docker Hub, as `docker.io/library/cafe-api`: only Docker's official images live in `library`, so the push is denied.
Tag the image with your registry and namespace first (`docker tag`) (lessons 076, 077).

</details>

**3. What is the difference between a tag and a digest?**

<details><summary>Answer</summary>

A tag is a movable name that can point to a different image tomorrow; a digest (`@sha256:…`) identifies the exact
content and never changes (lessons 075, 076).

</details>

**4. What do `no basic auth credentials`, `401 Unauthorized` and `denied` each tell you?**

<details><summary>Answer</summary>

Not logged in to that registry; a credential was sent and rejected (wrong or expired); authenticated but no permission
for the repository (lesson 078).

</details>

**5. Why should scripts use `docker login --password-stdin`?**

<details><summary>Answer</summary>

A password or token on the command line is visible in the shell history and the process list; standard input is not
(lessons 076, 078).

</details>

**6. A GitHub Actions workflow fails to push to `ghcr.io` with `GITHUB_TOKEN`. What do you check first?**

<details><summary>Answer</summary>

That the workflow grants `permissions: packages: write`, that the image name is `ghcr.io/<owner, lowercase>/…` for the
repository's owner, and, for an existing package, that the repository has write access to it (lesson 079).

</details>

**7. Why is `latest` a bad tag to deploy?**

<details><summary>Answer</summary>

It moves with every push and says nothing about the version: two servers can run different code under the same name,
and a rollback has no target. Deploy full versions or digests (lessons 076, 077, 021).

</details>

## Practical task

Run a private registry on port 5000, publish `alpine:3.23` there as `platform/base:3.23` **and** `platform/base:stable`,
remove both local names, and pull the image back by its **digest**.

<details><summary>Solution</summary>

<!-- test: anyof=Downloaded newer image||Image is up to date; output -->
```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker tag alpine:3.23 localhost:5000/platform/base:3.23
docker tag alpine:3.23 localhost:5000/platform/base:stable
docker push -q --all-tags localhost:5000/platform/base > /dev/null
accept='Accept: application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'
digest=$(curl -sI -H "$accept" localhost:5000/v2/platform/base/manifests/3.23 | grep -i docker-content-digest | tr -d '\r' | cut -d' ' -f2)
echo "digest: $digest"
docker image rm localhost:5000/platform/base:3.23 localhost:5000/platform/base:stable > /dev/null
docker pull "localhost:5000/platform/base@$digest" 2>&1 | grep Status
```

```text
digest: sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
Status: Downloaded newer image for localhost:5000/platform/base@sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
```

The registry reports the manifest's digest in the `Docker-Content-Digest` header (lesson 075). The reference
`REPOSITORY@sha256:…` keeps working whatever happens to the tags.

<!-- test -->
```bash
docker rm -f registry > /dev/null
docker image ls --digests --format '{{.Repository}}@{{.Digest}}' | grep '^localhost:5000/platform/base@' | while read -r ref; do docker image rm "$ref" > /dev/null; done
```

</details>

## Troubleshooting task

A deployment script fails. Reproduce the situation:

<!-- test: fail; contains=not found; output -->
```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker tag busybox:1.37 localhost:5000/shop/worker:2.1.0
docker push -q localhost:5000/shop/worker:2.1.0 > /dev/null
docker pull localhost:5000/shop/worker:v2.1.0 2>&1
```

```text
Error response from daemon: failed to resolve reference "localhost:5000/shop/worker:v2.1.0": localhost:5000/shop/worker:v2.1.0: not found
```

Find the cause and fix it.

<details><summary>Solution</summary>

`manifest unknown`: the registry is reachable and needs no credentials, but the tag does not exist. List the tags:

<!-- test: contains=2.1.0; output -->
```bash
curl -s localhost:5000/v2/shop/worker/tags/list; echo
```

```text
{"name":"shop/worker","tags":["2.1.0"]}
```

The image was pushed as `2.1.0`, the script asks for `v2.1.0` (the Git tag, not the image tag). Fix the script to strip
the `v`, as `${GITHUB_REF_NAME#v}` does in lesson 079:

<!-- test: contains=localhost:5000/shop/worker:2.1.0 -->
```bash
ref=v2.1.0
docker pull -q "localhost:5000/shop/worker:${ref#v}"
```

<!-- test -->
```bash
docker rm -f registry > /dev/null
docker image rm localhost:5000/shop/worker:2.1.0 > /dev/null
```

</details>

## Real-world scenario

Your company's CI jobs started failing during busy hours with `toomanyrequests: You have reached your unauthenticated
pull rate limit`. Every job pulls `node:24-alpine` and `postgres:18-alpine` from Docker Hub. What is happening, and what
would you set up?

<details><summary>Model answer</summary>

All CI runners share a few public IP addresses, and Docker Hub limits anonymous pulls per address; busy hours exhaust
the limit (lesson 076, troubleshooting problem 25). Short term: log in to Docker Hub in CI with an organisation's
read-only access token (higher limits). Long term: pull base images through the company's own registry, as a
pull-through cache or by mirroring the pinned base images (lesson 078), and pin them by version or digest. Builds then
no longer depend on Docker Hub's limits or availability.

</details>

## Cleanup

Each task above removes its registry and images.
