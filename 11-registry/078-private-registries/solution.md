<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 078 · Private registries · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Add a second user `ci-bot` (password `another-example-change-me`) to the registry without restarting it, and prove
that it can log in. (The `htpasswd` file is read again when it changes.)

## Solution

```bash
cd ~/docker-practice/lesson-078
docker run --rm alpine:3.23 sh -c 'apk add -q apache2-utils > /dev/null && htpasswd -Bbn ci-bot another-example-change-me' >> auth/htpasswd
sleep 1
echo "another-example-change-me" | docker login localhost:5001 -u ci-bot --password-stdin 2>&1
```

```text
Login Succeeded
```

One user per person or machine makes it possible to revoke a single credential (a leaked CI token) without changing
everyone's. Managed registries go further with per-repository permissions and short-lived tokens.
