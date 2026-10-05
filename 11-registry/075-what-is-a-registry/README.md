# Lesson 075 · What is a registry?

> Level 12 · Registries · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A **registry** is a server that stores images and hands them out: `docker push` uploads an image, `docker pull`
downloads it. It is how an image built on one machine (a laptop, a CI runner) reaches every other machine (servers,
Kubernetes nodes). Docker Hub is the default registry; GitHub, GitLab and every cloud run their own; and you can run
one yourself, with the official `registry` image. This lesson does exactly that, on your computer.

## Visual

```text
  build machine                      registry  localhost:5000                 any other machine
 ┌───────────────┐   docker push    ┌──────────────────────────────┐ docker pull ┌───────────────┐
 │ image         │ ───────────────▶ │ repository  cafe/alpine      │ ──────────▶ │ image         │
 │ localhost:5000│   layers that    │   tags  3.23 → manifest      │  only the   │ same digest   │
 │ /cafe/alpine  │   are missing    │   layers (blobs, shared)     │  missing    │               │
 │ :3.23         │                  │ HTTP API  /v2/…              │  layers     │               │
 └───────────────┘                  └──────────────────────────────┘             └───────────────┘

 the image name says where it lives:  localhost:5000 / cafe/alpine : 3.23
                                      registry        repository    tag
```

## Lab setup

Start a private registry in a container, on port 5000:

<!-- test: contains=running -->
```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker inspect registry --format '{{.Name}}: {{.State.Status}}'
```

## Demonstration

An image can only be pushed to the registry its **name** points to. Give a local image a second name that starts with
the registry's address:

<!-- test: contains=localhost:5000/cafe/alpine; output -->
```bash
docker tag alpine:3.23 localhost:5000/cafe/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep alpine
```

```text
python:3.14-alpine  f6a589d43c42
eclipse-temurin:25-jre-alpine  3c0a9084927a
eclipse-temurin:25-jdk-alpine  3fd2d245c4e0
php:8.5-fpm-alpine  fa01fb1645cd
nginx:1.30-alpine  0985e772fb9f
redis:8-alpine  3811787313eb
node:24-alpine  ebfe2f904627
golang:1.26-alpine  8ac98ca534ac
postgres:18-alpine  77f585114c32
alpine:3.23  85fe1e81d675
localhost:5000/cafe/alpine:3.23  85fe1e81d675
nginx:1.29-alpine  5616878291a2
```

Two names, one image (the same ID). Push it:

<!-- test: contains=digest: sha256; output -->
```bash
docker push localhost:5000/cafe/alpine:3.23
```

```text
The push refers to repository [localhost:5000/cafe/alpine]
d0c1d894c237: Unavailable
d0c1d894c237: Unavailable
d0c1d894c237: Unavailable
d0c1d894c237: Unavailable
d0c1d894c237: Unavailable
d0c1d894c237: Unavailable
d0c1d894c237: Pushed
3.23: digest: sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15 size: 1022

 Info -> Not all multiplatform-content is present and only the available single-platform image was pushed
         sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0 -> sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
```

A registry is an HTTP API. Ask it what it stores:

<!-- test: contains=cafe/alpine; output -->
```bash
curl -s localhost:5000/v2/_catalog
curl -s localhost:5000/v2/cafe/alpine/tags/list
```

```text
{"repositories":["cafe/alpine"]}
{"name":"cafe/alpine","tags":["3.23"]}
```

Remove the local copy and pull it back, as another machine would:

<!-- test: contains=Downloaded newer image; output -->
```bash
docker image rm localhost:5000/cafe/alpine:3.23 > /dev/null
docker pull localhost:5000/cafe/alpine:3.23
```

```text
3.23: Pulling from cafe/alpine
Digest: sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
Status: Downloaded newer image for localhost:5000/cafe/alpine:3.23
localhost:5000/cafe/alpine:3.23
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker run -d -p 5000:5000 registry:3` | a private registry (the CNCF Distribution project) |
| `docker tag SOURCE TARGET` | give an image another name (no copy) |
| `docker push NAME:TAG` | upload the image to the registry in its name |
| `docker pull NAME:TAG` | download it |
| `GET /v2/_catalog` | the repositories of the registry |
| `GET /v2/REPO/tags/list` | the tags of a repository |

## Hands-on lab

**Instructions.** Push `busybox:1.37` to your registry as `localhost:5000/tools/busybox:1.37`, and list the
repositories of the registry.

**Expected result.** The catalog lists `cafe/alpine` and `tools/busybox`.

**Verification.**

<!-- test: contains=tools/busybox -->
```bash
docker tag busybox:1.37 localhost:5000/tools/busybox:1.37
docker push -q localhost:5000/tools/busybox:1.37
curl -s localhost:5000/v2/_catalog
```

## Break it

A teammate pulls the version they expect to be there:

<!-- test: fail; contains=not found; output -->
```bash
docker pull localhost:5000/cafe/alpine:3.24 2>&1
```

```text
Error response from daemon: failed to resolve reference "localhost:5000/cafe/alpine:3.24": localhost:5000/cafe/alpine:3.24: not found
```

## Troubleshoot it

`manifest unknown`: the registry answered (so address, network and authentication are fine), but it has no image with
that tag. Ask the registry which tags exist:

<!-- test: contains=3.23; output -->
```bash
curl -s localhost:5000/v2/cafe/alpine/tags/list
```

```text
{"name":"cafe/alpine","tags":["3.23"]}
```

The tag was never pushed. Other answers mean other problems: `connection refused` or a timeout (wrong address, registry
down), `unauthorized` (lesson 078), `429 Too Many Requests` (a rate limit, troubleshooting problem 25).

## Fix it

Pull a tag that exists, or push the missing one first:

<!-- test: contains=localhost:5000/cafe/alpine:3.23 -->
```bash
docker pull -q localhost:5000/cafe/alpine:3.23
```

## Practice challenge

Push the same image under a second tag `stable`, and show with the registry API that both tags point to the **same**
manifest digest (ask for the manifest with a `HEAD` request and read the `Docker-Content-Digest` header).

<details>
<summary>Solution</summary>

<!-- test: contains=same digest; output -->
```bash
docker tag localhost:5000/cafe/alpine:3.23 localhost:5000/cafe/alpine:stable
docker push -q localhost:5000/cafe/alpine:stable > /dev/null
accept='Accept: application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'
a=$(curl -sI -H "$accept" localhost:5000/v2/cafe/alpine/manifests/3.23 | grep -i docker-content-digest | tr -d '\r')
b=$(curl -sI -H "$accept" localhost:5000/v2/cafe/alpine/manifests/stable | grep -i docker-content-digest | tr -d '\r')
echo "$a"; echo "$b"
[ "$a" = "$b" ] && echo "same digest"
```

```text
Docker-Content-Digest: sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
Docker-Content-Digest: sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
same digest
```

Tags are labels that point to a manifest; the digest identifies the content. The push sent no layers: the registry
already had them.

</details>

## Real-world example

A company's CI builds every commit into an image and pushes it to the company registry. Staging and production servers
(or Kubernetes) pull from that registry; nobody copies image files around. The registry is also where retention rules
delete old tags, where images are scanned for vulnerabilities, and where access is controlled.

## Recap

- A registry stores images as repositories with tags; push uploads, pull downloads (only missing layers).
- The image's name decides the registry: `REGISTRY/REPOSITORY:TAG`.
- `registry:3` runs a private registry; its HTTP API (`/v2/…`) shows repositories and tags.
- `manifest unknown` = the registry works, the tag does not exist.

## Cleanup

<!-- test -->
```bash
docker rm -f registry > /dev/null
docker image rm localhost:5000/cafe/alpine:3.23 localhost:5000/cafe/alpine:stable localhost:5000/tools/busybox:1.37 > /dev/null
```

Next: [Lesson 076 · Docker Hub](../076-docker-hub/README.md)
