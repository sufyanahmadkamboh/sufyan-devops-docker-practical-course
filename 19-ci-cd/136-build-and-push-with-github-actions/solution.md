<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 136 · Build and push with GitHub Actions · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Pull requests must never push. Show, from the workflow file, which expression prevents it, and which step is skipped
entirely for pull requests.

## Solution

```bash
cd ~/docker-practice/lesson-136
grep -n "pull_request" .github/workflows/docker-image.yml
```

```text
9:  pull_request:
41:        if: github.event_name != 'pull_request'
52:          push: ${{ github.event_name != 'pull_request' }}
```

The login step has `if: github.event_name != 'pull_request'` (it is skipped), and the build step pushes only when
`push:` evaluates to `true`, which is false for pull requests. Pull requests from forks also get a read-only token,
so even a modified workflow could not push.
