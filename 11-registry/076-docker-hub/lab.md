<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 076 · Docker Hub · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find out whether this Docker client has stored Docker Hub credentials: look at the client
configuration file `~/.docker/config.json`.

**Expected result.** Either no file / no `auths` entry (never logged in), or an `auths` entry for
`https://index.docker.io/v1/`, usually with a `credsStore` (the credentials themselves are kept by the operating
system's credential store, not in the file).

**Verification.**

```bash
if grep -q '"auths"' ~/.docker/config.json 2> /dev/null && grep -q 'index.docker.io' ~/.docker/config.json; then
  echo "saved logins: Docker Hub"
else
  echo "saved logins: none for Docker Hub"
fi
```
