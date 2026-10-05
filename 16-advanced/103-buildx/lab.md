<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 103 · BuildKit and buildx · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show how much disk the build cache uses now, then build only the `build` stage with
`--target build` and load it as `cafe-go:build-stage`. Compare its size with `cafe-go:1.0`.

**Expected result.** The build stage (Go toolchain included) is many times larger than the final image.

**Verification.**

```bash
docker buildx du | tail -1
docker buildx build -q --target build -t cafe-go:build-stage --load . > /dev/null
for image in cafe-go:build-stage cafe-go:1.0; do
  echo "$image $(docker image inspect --format '{{.Size}}' "$image" | awk '{printf "%.1f MB", $1/1000000}')"
done
```
