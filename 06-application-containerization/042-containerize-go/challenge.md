<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 042 · Containerizing a Go application · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Go cross-compiles by setting `GOOS` and `GOARCH`. Without installing Go, build an **arm64** Linux binary of the API into
the lab folder (a bind mount, `-v "$(pwd):/src"`), and let the Go tool confirm its architecture with `go version -m`.

The solution is in [solution.md](solution.md).
