<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 079 · GitHub Container Registry · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Push without logging in:

```bash
docker push ghcr.io/cafe-team-example/cafe-api:1.0 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
denied
```

## Troubleshoot it

GHCR refuses anonymous pushes. With a login, three more causes give similar messages:

| Message after `docker login ghcr.io` | Cause | Fix |
|---|---|---|
| `denied: permission_denied: The token provided does not match expected scopes` | token without `write:packages` | new token, or `gh auth refresh -s write:packages` |
| `denied: permission_denied: write_package` | the owner in the name is not you or your organisation, or the workflow lacks `packages: write` | correct the name / add the permission |
| `denied: installation not allowed to Write organization package` | the package exists and is not connected to this repository | in the package settings, give the repository write access |

Check what this client has stored for ghcr.io, and which scopes the GitHub CLI's token has:

```bash
grep -q '"ghcr.io"' ~/.docker/config.json 2> /dev/null && echo "ghcr.io login stored: yes" || echo "ghcr.io login stored: no"
```

```text
ghcr.io login stored: no
```

```bash
gh auth status          # lists "Token scopes: … write:packages …" when the scope is there
```

## Fix it

Log in with a token that has `write:packages`, and push to your own namespace:

```bash
gh auth token | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
docker tag ghcr.io/cafe-team-example/cafe-api:1.0 ghcr.io/your_github_user/cafe-api:1.0
docker push ghcr.io/your_github_user/cafe-api:1.0
```
