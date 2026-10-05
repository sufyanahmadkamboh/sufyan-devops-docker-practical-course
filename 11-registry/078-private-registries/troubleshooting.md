<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 078 · Private registries · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Logged out, a deployment tries to pull the image:

```bash
docker image rm localhost:5001/cafe/api:1.0 > /dev/null
docker pull localhost:5001/cafe/api:1.0 2>&1
```

```text
Error response from daemon: failed to resolve reference "localhost:5001/cafe/api:1.0": pull access denied, repository does not exist or may require authorization: authorization failed: no basic auth credentials
```

And someone logs in with a wrong password:

```bash
echo "wrong-password" | docker login localhost:5001 -u student --password-stdin 2>&1
```

```text
Error response from daemon: login attempt to http://localhost:5001/v2/ failed with status: 401 Unauthorized
```

## Troubleshoot it

Two different messages, two different causes:

| Message | Meaning |
|---|---|
| `no basic auth credentials` | the client has **no** credential for this registry: not logged in (on this machine, as this user) |
| `401 Unauthorized` / `unauthorized: authentication required` | a credential was sent and **rejected**: wrong user, password or expired token |
| `denied: requested access to the resource is denied` | authenticated, but **no permission** for this repository |

Check what the client has stored for the registry, and test the credential directly against the API:

```bash
grep -q '"localhost:5001":' ~/.docker/config.json && echo "stored: yes" || echo "stored: no"
curl -s -w '\nHTTP %{http_code}\n' -u student:wrong-password localhost:5001/v2/ | tail -1
```

```text
stored: no
HTTP 401
```

## Fix it

Log in with valid credentials, then pull:

```bash
echo "example-password-change-me" | docker login localhost:5001 -u student --password-stdin > /dev/null 2>&1
docker pull -q localhost:5001/cafe/api:1.0
```

On cloud registries the password is a short-lived token from the cloud CLI, so "it worked yesterday" is often an
expired login. For example:

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.eu-central-1.amazonaws.com
az acr login --name cafe-registry
gcloud auth configure-docker europe-west3-docker.pkg.dev
```
