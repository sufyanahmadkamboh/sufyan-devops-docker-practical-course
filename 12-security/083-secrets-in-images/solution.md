<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 083 · Secrets in images · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The application needs `DB_PASSWORD` at run time. Remove it from the image entirely and provide it when the container
starts, from a file, so the password is not in the image and not in your shell history. Prove that the image has no
`DB_PASSWORD`, but the container does.

## Solution

```bash
printf 'DB_PASSWORD=example-password-change-me\n' > db.env
docker image inspect --format '{{.Config.Env}}' cafe-secrets:fixed | grep -q DB_PASSWORD || echo "image: no DB_PASSWORD"
echo "container: $(docker run --rm --env-file db.env cafe-secrets:fixed sh -c 'env | grep DB_PASSWORD')"
```

```text
image: no DB_PASSWORD
container: DB_PASSWORD=example-password-change-me
```

`--env-file` (lesson 060) keeps the value out of the image and the command line. Note that environment variables are
still visible with `docker inspect` on the **container**: for real secrets, prefer secret files mounted at run time
(Compose and Kubernetes secrets, lesson 061).
