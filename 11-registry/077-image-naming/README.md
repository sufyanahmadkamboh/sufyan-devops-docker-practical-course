# Lesson 077 · Image naming

> Level 12 · Registries · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

An image name is an address: **registry / namespace / repository : tag**, optionally **@digest**. Every part except
the repository has a default, which is why `nginx` works. Knowing the parts tells you where `docker push` will send an
image, and good tags tell everyone which version it is. One image can have many names; `docker tag` adds one, without
copying anything.

## Visual

```text
   ghcr.io  /  cafe-team  /  cafe-api  :  1.4.2  @sha256:3f1a…
   ───────     ─────────     ────────     ─────   ───────────────
   registry    namespace     repository   tag     digest (content address, immutable)
   (default    (default for  (required)   (default
   docker.io)  Docker Hub:                latest)
                library)

 rules: lowercase letters, digits, separators . _ - in names; a tag is up to 128 of [A-Za-z0-9_.-]
 one image ── many names:  cafe-api:1.4.2  cafe-api:1.4  cafe-api:1  cafe-api:sha-3f1a2b4
```

## Lab setup

A local registry to push names to:

<!-- test: contains=running -->
```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker inspect registry --format '{{.State.Status}}'
```

## Demonstration

Give one image several names, the way a release is tagged:

<!-- test: contains=localhost:5000/cafe-team/cafe-api; output -->
```bash
for tag in 1.4.2 1.4 1; do docker tag busybox:1.37 localhost:5000/cafe-team/cafe-api:$tag; done
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep -E "busybox|cafe-api" | sort
```

```text
busybox:1.37  bdf57e528e45
localhost:5000/cafe-team/cafe-api:1  bdf57e528e45
localhost:5000/cafe-team/cafe-api:1.4  bdf57e528e45
localhost:5000/cafe-team/cafe-api:1.4.2  bdf57e528e45
```

Four names, one ID: one image on disk. Pushing all tags of a repository at once (`--all-tags`):

<!-- test: contains=1.4.2; output -->
```bash
docker push -q --all-tags localhost:5000/cafe-team/cafe-api > /dev/null
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

```text
{"name":"cafe-team/cafe-api","tags":["1","1.4","1.4.2"]}
```

How Docker expands names (`docker image inspect` shows the repository it recorded, `docker pull` uses the full form):

| You write | Registry | Namespace / repository | Tag |
|---|---|---|---|
| `redis` | `docker.io` | `library/redis` | `latest` |
| `redis:8-alpine` | `docker.io` | `library/redis` | `8-alpine` |
| `bitnami/redis:8` | `docker.io` | `bitnami/redis` | `8` |
| `ghcr.io/cafe-team/cafe-api:1.4.2` | `ghcr.io` | `cafe-team/cafe-api` | `1.4.2` |
| `localhost:5000/cafe-team/cafe-api:1` | `localhost:5000` | `cafe-team/cafe-api` | `1` |

The first part counts as a registry only when it contains a `.` or a `:`, or is `localhost`.

## Command breakdown

| Command | What it does |
|---|---|
| `docker tag SOURCE[:TAG] TARGET[:TAG]` | add a name to an existing image |
| `docker push --all-tags REPOSITORY` | push every local tag of that repository |
| `docker image rm NAME:TAG` | remove one name; the image goes only when its last name is removed |
| `IMAGE@sha256:…` | refer to exact content, whatever the tags say |

## Hands-on lab

**Instructions.** Add the tag `sha-3f1a2b4` (a short Git commit, as CI pipelines do) to the same image, push it, and list
the repository's tags.

**Expected result.** Four tags: `1`, `1.4`, `1.4.2`, `sha-3f1a2b4`.

**Verification.**

<!-- test: contains=sha-3f1a2b4 -->
```bash
docker tag localhost:5000/cafe-team/cafe-api:1.4.2 localhost:5000/cafe-team/cafe-api:sha-3f1a2b4
docker push -q localhost:5000/cafe-team/cafe-api:sha-3f1a2b4
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

## Break it

A teammate names the image after the product's spelling:

<!-- test: fail; contains=must be lowercase; output -->
```bash
docker tag busybox:1.37 localhost:5000/CafeTeam/CafeAPI:1.4.2 2>&1
```

```text
error parsing reference: "localhost:5000/CafeTeam/CafeAPI:1.4.2" is not a valid repository/tag: invalid reference format: repository name (CafeTeam/CafeAPI) must be lowercase
```

## Troubleshoot it

`invalid reference format: repository name … must be lowercase`: the registry part may contain capitals (host names are
case-insensitive), the repository path may not. Tags may (`1.4.2-RC1` is valid). Other `invalid reference format`
causes are characters outside the allowed set: a space, a second `:` in the tag, a leading `-`.

<!-- test: contains=valid; output -->
```bash
for name in cafe-api:1.4.2-RC1 cafe_api:1.4.2 "cafe api:1.4.2" cafe-api:1.4:2; do
  docker tag busybox:1.37 "$name" 2> /dev/null && echo "valid:   $name" || echo "invalid: $name"
done
docker image rm cafe-api:1.4.2-RC1 cafe_api:1.4.2 > /dev/null
```

```text
valid:   cafe-api:1.4.2-RC1
valid:   cafe_api:1.4.2
invalid: cafe api:1.4.2
invalid: cafe-api:1.4:2
```

## Fix it

<!-- test: contains=cafeteam/cafe-api -->
```bash
docker tag busybox:1.37 localhost:5000/cafeteam/cafe-api:1.4.2
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep cafeteam
```

## Practice challenge

Remove the tag `localhost:5000/cafe-team/cafe-api:1` locally and show that the image is still there under its other
names. Then show which tag names in the registry are unaffected.

<details>
<summary>Solution</summary>

<!-- test: contains=Untagged; contains="1"; output -->
```bash
docker image rm localhost:5000/cafe-team/cafe-api:1
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -c "cafe-team/cafe-api"
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

```text
Untagged: localhost:5000/cafe-team/cafe-api:1
3
{"name":"cafe-team/cafe-api","tags":["1","1.4","1.4.2","sha-3f1a2b4"]}
```

`Untagged`, not `Deleted`: only the name went, the image keeps its other names. The registry is independent of your
local names: its tag `1` is still there.

</details>

## Real-world example

A team's release pipeline tags each image with the full version (`1.4.2`, never moved), the moving minor and major tags
(`1.4`, `1`) for consumers who want updates within a range, and the Git commit (`sha-3f1a2b4`) to trace any running
container back to its source. Deployments use the full version or the digest; `latest` is never deployed.

## Recap

- `registry/namespace/repository:tag@digest`; defaults: `docker.io`, `library`, `latest`.
- Repository names are lowercase; tags allow `[A-Za-z0-9_.-]`, up to 128 characters.
- `docker tag` adds a name; one image can have many; `rm` of a name only untags.
- Tag releases with full versions and commits; pin deployments to versions or digests.

## Cleanup

<!-- test -->
```bash
docker rm -f registry > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -E "^localhost:5000/" | xargs docker image rm > /dev/null
```

Next: [Lesson 078 · Private registries](../078-private-registries/README.md)
