<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 020 · Image tags · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Release `1.5.0`: build it, and move only the tags that should follow it. Then prove that `cafe-menu:1.4` still gives
the newest **1.4** release and `cafe-menu:1` gives 1.5.0.

## Solution

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
