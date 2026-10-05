<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 076 · Docker Hub · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Try to publish without logging in:

```bash
docker tag alpine:3.23 cafe-student/cafe-api:1.0
docker push cafe-student/cafe-api:1.0 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
```

## Troubleshoot it

`push access denied … may require authorization`: Docker Hub refuses anonymous pushes, and you can only push into a
namespace you own (your user name or an organisation you belong to). The message is the same whether the repository
does not exist or you lack permission: registries do not reveal which private repositories exist. Check the two
conditions:

```bash
echo "namespace in the image name: $(echo cafe-student/cafe-api:1.0 | cut -d/ -f1)"
grep -q 'index.docker.io' ~/.docker/config.json 2> /dev/null && echo "logged in: yes" || echo "logged in: no"
```

```text
namespace in the image name: cafe-student
logged in: no
```

## Fix it

Log in as the owner of the namespace (with a token that allows writing), and name the image with your namespace:

```bash
echo "$DOCKERHUB_TOKEN" | docker login -u YOUR_USER --password-stdin
docker tag alpine:3.23 YOUR_USER/cafe-api:1.0
docker push YOUR_USER/cafe-api:1.0
```

Remove the practice tag:

```bash
docker image rm cafe-student/cafe-api:1.0 > /dev/null
```
