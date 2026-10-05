# Lesson 078 · Private registries

> Level 12 · Registries · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

Company images belong in a **private registry**: only people and machines with credentials may push or pull. It can be
a managed service (Amazon ECR, Azure Container Registry, Google Artifact Registry, GitHub, GitLab, Harbor, Nexus …) or
the `registry` image you already know, with authentication switched on. Whatever the product, the client side is the
same: `docker login REGISTRY`, then push and pull with names that start with that registry.

## Visual

```text
 docker login localhost:5001 ──── user + password/token ───▶ registry checks htpasswd ─▶ "Login Succeeded"
        │
        └─ stores the credential (credential store, or base64 in ~/.docker/config.json)

 docker push localhost:5001/cafe/api:1.0
        │  sends the stored credential with every request
        ▼
 ┌──────────────── registry:3  (REGISTRY_AUTH=htpasswd) ────────────────┐
 │  no / wrong credential  → 401 unauthorized                           │
 │  valid credential       → push / pull                                │
 └──────────────────────────────────────────────────────────────────────┘
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-078
cd ~/docker-practice/lesson-078
mkdir auth
```

Create a user for the registry. `htpasswd` (from Apache's tools) writes the user and a bcrypt hash of the password;
it runs in a throw-away Alpine container, so you install nothing. The password is a practice value: never reuse a
real one in examples.

<!-- test: contains=student:$2y$; output=head:1 -->
```bash
docker run --rm alpine:3.23 sh -c 'apk add -q apache2-utils > /dev/null && htpasswd -Bbn student example-password-change-me' > auth/htpasswd
cut -c1-20 auth/htpasswd
```

```text
student:$2y$05$yig0j
```

Start a registry that requires it, on port 5001:

<!-- test: contains=running -->
```bash
docker run -d --name private-registry -p 5001:5000 \
  -v "$(pwd)/auth:/auth:ro" \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Cafe registry" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  registry:3 > /dev/null
sleep 2
docker inspect private-registry --format '{{.State.Status}}'
```

## Demonstration

Without credentials, the registry answers `401`:

<!-- test: contains=401; output -->
```bash
curl -s -w '\nHTTP %{http_code}\n' localhost:5001/v2/ | tail -1
curl -s -w '\nHTTP %{http_code}\n' -u student:example-password-change-me localhost:5001/v2/ | tail -1
```

```text
HTTP 401
HTTP 200
```

Log in the way scripts and CI do, with the password on standard input:

<!-- test: contains=Login Succeeded; output -->
```bash
echo "example-password-change-me" | docker login localhost:5001 -u student --password-stdin 2>&1
```

```text
Login Succeeded
```

Push and pull work now:

<!-- test: contains=cafe/api; output -->
```bash
docker tag alpine:3.23 localhost:5001/cafe/api:1.0
docker push -q localhost:5001/cafe/api:1.0
curl -s -u student:example-password-change-me localhost:5001/v2/_catalog
```

```text
localhost:5001/cafe/api:1.0

 Info -> Not all multiplatform-content is present and only the available single-platform image was pushed
         sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0 -> sha256:1f3591b8a02ea153f41c5bba878ad477f63ab3d19349762cb77504db02a23e15
{"repositories":["cafe/api"]}
```

The `Info` line is Docker telling you that `alpine:3.23` is a multi-platform image and only the platform present on
your computer was pushed (lesson 104 covers multi-platform images).

Where did the login go? Look at the registry's entry in the client configuration:

<!-- test: contains=localhost:5001; output -->
```bash
grep -o '"localhost:5001": {[^}]*}' ~/.docker/config.json | sed 's/"auth": "[^"]*"/"auth": "…"/'
```

```text
"localhost:5001": {}
```

An empty entry `{}` means a **credential helper** holds the secret in the operating system's keychain (Docker Desktop
installs one). Without a helper, typically on a Linux server, the entry holds `"auth": "…"`, the user and password only
base64-encoded, and `docker login` warns `Your credentials are stored unencrypted`. Base64 is an encoding, not
encryption: anyone who can read that file has the password.

## Command breakdown

| Command / setting | What it does |
|---|---|
| `htpasswd -Bbn USER PASSWORD` | print a user line with a bcrypt hash (`-B`), from the command line (`-b`), to stdout (`-n`) |
| `REGISTRY_AUTH=htpasswd`, `…_PATH`, `…_REALM` | switch on basic authentication in `registry:3` |
| `docker login REGISTRY -u USER --password-stdin` | log in to that registry |
| `docker logout REGISTRY` | remove its stored credential |
| `credsStore` / `credHelpers` in `config.json` | keep credentials in a keychain, or get them from a cloud CLI |

## Hands-on lab

**Instructions.** Log out of the private registry and check that its entry has disappeared from `config.json`.

**Expected result.** `Removing login credentials for localhost:5001`, and no `localhost:5001` in the file.

**Verification.**

<!-- test: contains=Removing login credentials; absent=localhost:5001": -->
```bash
docker logout localhost:5001
grep -c '"localhost:5001":' ~/.docker/config.json || true
```

## Break it

Logged out, a deployment tries to pull the image:

<!-- test: fail; anyof=no basic auth credentials||unauthorized; output -->
```bash
docker image rm localhost:5001/cafe/api:1.0 > /dev/null
docker pull localhost:5001/cafe/api:1.0 2>&1
```

```text
Error response from daemon: failed to resolve reference "localhost:5001/cafe/api:1.0": pull access denied, repository does not exist or may require authorization: authorization failed: no basic auth credentials
```

And someone logs in with a wrong password:

<!-- test: fail; contains=401 Unauthorized; output -->
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

<!-- test: contains=HTTP 401; output -->
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

<!-- test: contains=localhost:5001/cafe/api:1.0 -->
```bash
echo "example-password-change-me" | docker login localhost:5001 -u student --password-stdin > /dev/null 2>&1
docker pull -q localhost:5001/cafe/api:1.0
```

On cloud registries the password is a short-lived token from the cloud CLI, so "it worked yesterday" is often an
expired login. For example:

<!-- test: skip -->
```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.eu-central-1.amazonaws.com
az acr login --name cafe-registry
gcloud auth configure-docker europe-west3-docker.pkg.dev
```

## Practice challenge

Add a second user `ci-bot` (password `another-example-change-me`) to the registry without restarting it, and prove
that it can log in. (The `htpasswd` file is read again when it changes.)

<details>
<summary>Solution</summary>

<!-- test: contains=Login Succeeded; output=tail:1 -->
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

</details>

## Real-world example

A company runs its images in Amazon ECR. Developers never handle passwords: `aws ecr get-login-password` exchanges
their single sign-on session for a token valid 12 hours. Servers and Kubernetes nodes pull through an IAM role, CI pushes
through a role trusted by GitHub's OIDC tokens. The registry also acts as a pull-through cache for Docker Hub, so base
images come from inside the company network.

## Recap

- A private registry requires credentials: `docker login REGISTRY`, then push/pull by its name.
- `registry:3` supports htpasswd authentication; managed registries use tokens from their CLI.
- `no basic auth credentials` = not logged in; `401 Unauthorized` = rejected; `denied` = no permission.
- Use `--password-stdin` and a credential helper; base64 in `config.json` is not protection.

## Cleanup

<!-- test -->
```bash
docker logout localhost:5001 > /dev/null 2>&1
docker rm -f private-registry > /dev/null
docker image rm localhost:5001/cafe/api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-078
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 079 · GitHub Container Registry](../079-github-container-registry/README.md)
