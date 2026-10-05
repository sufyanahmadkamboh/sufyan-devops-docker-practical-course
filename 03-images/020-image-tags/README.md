# Lesson 020 · Image tags

> Level 4 · Images · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

A **tag** is a movable name that points to an image ID, like a Git branch points to a commit. One image can have many
tags, and `docker image tag` adds one without copying anything. Teams use this for versioning: the exact version
`1.4.2` never moves, while the shorter `1.4` and `1` move to every new patch or minor release.

## Visual

```text
 after releasing 1.4.2                         after releasing 1.4.3

 cafe-menu:1.4.2 ──▶ image A                   cafe-menu:1.4.2 ──▶ image A   (exact version: never moves)
 cafe-menu:1.4   ──▶ image A                   cafe-menu:1.4.3 ──▶ image B
 cafe-menu:1     ──▶ image A                   cafe-menu:1.4   ──▶ image B   (moved)
                                               cafe-menu:1     ──▶ image B   (moved)

 tag format:  [REGISTRY[:PORT]/][NAMESPACE/]REPOSITORY[:TAG]
              repository: lowercase letters, digits, . _ - and /     tag: up to 128 of A-Z a-z 0-9 _ . -
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-020
cd ~/docker-practice/lesson-020
printf 'FROM alpine:3.23\nARG VERSION\nRUN echo "cafe menu $VERSION" > /version\nCMD ["cat", "/version"]\n' > Dockerfile
cat Dockerfile
```

A tiny image that prints its version (`ARG` is lesson 031).

## Demonstration

Build version 1.4.2 and give it the exact tag plus the two shorter ones:

<!-- test: contains=cafe-menu:1.4.2; output -->
```bash
docker build -q --build-arg VERSION=1.4.2 -t cafe-menu:1.4.2 . > /dev/null
docker image tag cafe-menu:1.4.2 cafe-menu:1.4
docker image tag cafe-menu:1.4.2 cafe-menu:1
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' cafe-menu
```

```text
cafe-menu:1  ffd4d7117e90
cafe-menu:1.4  ffd4d7117e90
cafe-menu:1.4.2  ffd4d7117e90
```

Three names, one image ID: tagging copied nothing. Now release the patch 1.4.3 and move the short tags to it:

<!-- test: contains=cafe menu 1.4.3; contains=cafe menu 1.4.2; output -->
```bash
docker build -q --build-arg VERSION=1.4.3 -t cafe-menu:1.4.3 . > /dev/null
docker image tag cafe-menu:1.4.3 cafe-menu:1.4
docker image tag cafe-menu:1.4.3 cafe-menu:1
for tag in 1.4.2 1.4.3 1.4 1; do echo "cafe-menu:$tag → $(docker run --rm cafe-menu:$tag)"; done
```

```text
cafe-menu:1.4.2 → cafe menu 1.4.2
cafe-menu:1.4.3 → cafe menu 1.4.3
cafe-menu:1.4 → cafe menu 1.4.3
cafe-menu:1 → cafe menu 1.4.3
```

`docker image tag` to an existing name simply moves it. Whoever deploys `cafe-menu:1.4.2` gets exactly that build;
whoever deploys `cafe-menu:1` gets the newest 1.x, whatever it is today.

A tag can also carry a registry address. This only names the image; nothing is uploaded until `docker push`
(lesson 076):

<!-- test: contains=localhost:5000/cafe/menu:1.4.3 -->
```bash
docker image tag cafe-menu:1.4.3 localhost:5000/cafe/menu:1.4.3
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' localhost:5000/cafe/menu
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker image tag SOURCE TARGET` (`docker tag`) | add the name TARGET to the image SOURCE; move it if it exists |
| `docker build -t NAME:TAG` | build and tag in one step; `-t` can be repeated |
| `docker image rm NAME:TAG` | remove one name (lesson 019) |
| no `:TAG` | means `:latest` (lesson 021) |

## Hands-on lab

**Instructions.** Build version `1.4.4` with **all three** tags in one `docker build` (repeat `-t`), and check that the
three names point to one ID.

**Expected result.** `cafe-menu:1.4.4`, `cafe-menu:1.4` and `cafe-menu:1` share one image ID.

**Verification.**

<!-- test: contains=one ID -->
```bash
cd ~/docker-practice/lesson-020
docker build -q --build-arg VERSION=1.4.4 -t cafe-menu:1.4.4 -t cafe-menu:1.4 -t cafe-menu:1 . > /dev/null
[ "$(docker image ls -q cafe-menu:1.4.4)" = "$(docker image ls -q cafe-menu:1)" ] && echo "one ID for 1.4.4, 1.4 and 1"
```

## Break it

The team wants a second image, the "Menu Board", and names it the way it is written in documents:

<!-- test: fail; contains=must be lowercase; output -->
```bash
docker image tag cafe-menu:1.4.4 Menu-Board:1.0
```

```text
error parsing reference: "Menu-Board:1.0" is not a valid repository/tag: invalid reference format: repository name (library/Menu-Board) must be lowercase
```

## Troubleshoot it

`invalid reference format: repository name … must be lowercase`: the repository part of an image name may only contain
lowercase letters, digits, and the separators `.`, `_`, `-` and `/`. The **tag** may contain uppercase letters, but
not `+`, `/` or spaces, and must not start with `.` or `-`. The same error appears in `docker build -t`, `docker run` and Compose files.
Test a name before using it:

<!-- test: contains=valid; output -->
```bash
for name in Menu-Board:1.0 menu-board:1.0+build7 menu-board:1.0-build7; do
  if docker image tag cafe-menu:1.4.4 "$name" 2> /dev/null; then echo "valid:   $name"; else echo "invalid: $name"; fi
done
```

```text
invalid: Menu-Board:1.0
invalid: menu-board:1.0+build7
valid:   menu-board:1.0-build7
```

## Fix it

Use a lowercase repository name:

<!-- test: contains=menu-board:1.0 -->
```bash
docker image tag cafe-menu:1.4.4 menu-board:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' menu-board
```

## Practice challenge

Release `1.5.0`: build it, and move only the tags that should follow it. Then prove that `cafe-menu:1.4` still gives
the newest **1.4** release and `cafe-menu:1` gives 1.5.0.

<details>
<summary>Solution</summary>

<!-- test: contains=1.4 → cafe menu 1.4.4; contains=1 → cafe menu 1.5.0; output -->
```bash
cd ~/docker-practice/lesson-020
docker build -q --build-arg VERSION=1.5.0 -t cafe-menu:1.5.0 -t cafe-menu:1.5 -t cafe-menu:1 . > /dev/null
for tag in 1.4 1.5 1; do echo "$tag → $(docker run --rm cafe-menu:$tag)"; done
```

```text
1.4 → cafe menu 1.4.4
1.5 → cafe menu 1.5.0
1 → cafe menu 1.5.0
```

`1.4` must not move to 1.5.0: someone who chose `1.4` asked for patches of 1.4 only. `1.5` is new; `1` follows the
newest 1.x.

</details>

## Real-world example

A CI pipeline tags every build with the Git commit (`cafe-menu:3f9c2ab`), which identifies the exact source of every
image, and adds a semantic version tag (`1.4.3`, `1.4`, `1`) when a release is published. Production deploys an exact
version or a digest, never a moving tag, so a deployment can always be reproduced and rolled back to the previous
exact version.

## Recap

- A tag is a movable name for an image ID; `docker image tag` adds or moves one and copies nothing.
- Exact versions (`1.4.2`) stay put; short tags (`1.4`, `1`) move to new releases.
- Repository names are lowercase; tags allow `A-Z a-z 0-9 _ . -`, up to 128 characters.
- A registry address in the name (`localhost:5000/cafe/menu`) decides where `docker push` sends it.

## Cleanup

<!-- test -->
```bash
docker image rm $(docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -e '^cafe-menu:' -e '^menu-board:' -e '^localhost:5000/cafe/menu:') > /dev/null
rm -rf ~/docker-practice/lesson-020
```

Next: [Lesson 021 · The danger of the latest tag](../021-latest-tag-danger/README.md)
