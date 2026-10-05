<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 135 · Docker in CI · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Tags in a registry should be **immutable**: version `1.0.0` must always mean the same image. Show that the image
pushed as `1.0.0` and the one pushed as `1.1.0` have different digests, and pull `1.0.0` back by its digest.

## Solution

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
