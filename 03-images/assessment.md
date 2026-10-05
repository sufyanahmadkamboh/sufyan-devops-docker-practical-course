# Module 03 assessment · Images

> Lessons [017](017-image-layers/README.md)–[021](021-latest-tag-danger/README.md) · ⏱ 30 minutes · try every
> question before opening its answer

## Knowledge check

**1. Which Dockerfile instructions create file layers, and which only change metadata?**

<details><summary>Answer</summary>

`RUN`, `COPY` and `ADD` create layers; `ENV`, `CMD`, `ENTRYPOINT`, `EXPOSE`, `LABEL`, `USER`, `WORKDIR` (apart from
creating the folder) only change the image's configuration (lesson 017).

</details>

**2. A Dockerfile downloads a 300 MB archive in one `RUN` and deletes it in the next. How much bigger is the image?**

<details><summary>Answer</summary>

About 300 MB: the first layer keeps the file; the second only hides it. Download, use and delete in the same `RUN`
(lesson 017).

</details>

**3. What does `alpine:3.23` expand to?**

<details><summary>Answer</summary>

`docker.io/library/alpine:3.23`: registry Docker Hub, namespace `library` (official images), repository `alpine`, tag
`3.23` (lesson 018).

</details>

**4. What is the difference between a tag and a digest?**

<details><summary>Answer</summary>

A tag is a movable name; it can point to a different image tomorrow. A digest (`@sha256:…`) is the hash of the
content and always refers to exactly the same image (lessons 018, 020).

</details>

**5. `docker image pull` fails with `429 Too Many Requests`. Is the image name wrong?**

<details><summary>Answer</summary>

No: it is Docker Hub's rate limit for anonymous requests. Wait, log in, or pull through a mirror; avoid unnecessary
pulls of images that are already present (lesson 018).

</details>

**6. Why does `docker image rm` refuse to delete an image that no container is running?**

<details><summary>Answer</summary>

A **stopped** container still uses it. Remove the container (`docker container ls -a --filter ancestor=…` finds it)
before the image (lesson 019).

</details>

**7. What is a dangling image, and what removes it?**

<details><summary>Answer</summary>

An image without a name (`<none>:<none>`), typically from a build without `-t` or a tag that moved to a newer build.
`docker image prune` removes dangling images; `docker image prune -a` removes every image no container uses
(lesson 019).

</details>

**8. Why is `image: cafe-menu:latest` a problem in a production deployment?**

<details><summary>Answer</summary>

`latest` moves with every untagged build or push, so different servers can run different versions, and there is no
record of which version ran or what to roll back to. Deploy exact versions or digests (lesson 021).

</details>

## Practical task

Build an image `cafe-board` from `alpine:3.23` that prints `today: soup of the day`, release it as version `2.3.1` with
the moving tags `2.3` and `2`, and prove that all three tags share one image ID while `cafe-board:latest` does not
exist.

<details><summary>Solution</summary>

<!-- test: contains=one ID; contains=no latest; output -->
```bash
mkdir -p ~/docker-practice/assessment-03 && cd ~/docker-practice/assessment-03
printf 'FROM alpine:3.23\nCMD ["echo", "today: soup of the day"]\n' > Dockerfile
docker build -q -t cafe-board:2.3.1 -t cafe-board:2.3 -t cafe-board:2 . > /dev/null
docker image ls --format '{{.ID}}' cafe-board | sort -u | wc -l | grep -q '^ *1$' && echo "one ID for 2.3.1, 2.3 and 2"
docker image inspect cafe-board:latest > /dev/null 2>&1 || echo "no latest: nobody can run an unversioned build by accident"
docker run --rm cafe-board:2
```

```text
one ID for 2.3.1, 2.3 and 2
no latest: nobody can run an unversioned build by accident
today: soup of the day
```

</details>

## Troubleshooting task

Prepare the situation:

<!-- test: fail; contains=conflict -->
```bash
cd ~/docker-practice/assessment-03
docker run --name board-check cafe-board:2.3.1 > /dev/null
docker image rm cafe-board:2.3.1 cafe-board:2.3 cafe-board:2 2>&1
```

A colleague wants to remove the release from this machine, and the removal of the last tag fails. Find out why, then
remove the release completely.

<details><summary>Solution</summary>

The first two names are only untagged; the last one fails with `conflict: unable to delete … container … is using its
referenced image`. The exited container `board-check` still needs the image:

<!-- test: contains=board-check; contains=removed -->
```bash
docker container ls -a --filter ancestor=cafe-board:2 --format '{{.Names}}  {{.Status}}'
docker rm board-check > /dev/null
docker image rm cafe-board:2 > /dev/null && echo "release removed"
```

</details>

## Real-world scenario

Your team's image has grown from 150 MB to 900 MB over three months, and deployments have become slow. Nobody knows
which change caused it. How do you find the cause, and which rules would you introduce?

<details><summary>Model answer</summary>

`docker image history --no-trunc` (or `--format '{{.Size}}\t{{.CreatedBy}}'`) on the current image shows the size of
each step: the large layer names the instruction responsible, typically a package cache, a downloaded archive deleted
in a later step, or a `COPY . .` that picked up build artefacts or test data (lesson 017). Comparing the history of an
older tag shows when it appeared. Rules: create and delete temporary files in the same `RUN`, clean package caches in
the same step, use `.dockerignore` (lesson 037), and check the image size in CI so growth is noticed in the pull request
that causes it.

</details>

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-board:2.3.1 cafe-board:2.3 cafe-board:2 > /dev/null 2>&1 || true
rm -rf ~/docker-practice/assessment-03
```
