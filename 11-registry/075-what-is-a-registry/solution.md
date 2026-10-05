<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 075 · What is a registry? · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Push the same image under a second tag `stable`, and show with the registry API that both tags point to the **same**
manifest digest (ask for the manifest with a `HEAD` request and read the `Docker-Content-Digest` header).

## Solution

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
