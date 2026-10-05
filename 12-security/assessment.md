# Module 12 assessment · Container security

> Lessons [080](080-attack-surface/README.md)–[086](086-resource-limits-for-security/README.md) · ⏱ 45 minutes ·
> try every question before opening its answer

## Knowledge check

**1. Why is `--privileged` dangerous even for a container you trust?**

<details><summary>Answer</summary>

It gives the container every capability and every host device: anyone who gets code execution inside it can mount the
host's disks and change the host. Trust in the image does not protect against a vulnerability in it (lesson 080).

</details>

**2. A container runs as root. Why does that matter if containers are isolated?**

<details><summary>Answer</summary>

User ID 0 in the container is user ID 0 for the shared kernel. After an escape (kernel bug, careless bind mount, the
Docker socket mounted) the attacker is root on the host. As a normal user they would not be (lesson 081).

</details>

**3. After adding `USER app`, the container exits with `Permission denied`. What is the correct fix?**

<details><summary>Answer</summary>

Give the user ownership of only the folders the application writes to (`RUN mkdir data && chown app:app data`), and
keep the code owned by root. Removing `USER` or `chmod 777` are not fixes (lesson 081).

</details>

**4. What is the difference between `python:3.14-slim` and `python:3.14-slim@sha256:…`?**

<details><summary>Answer</summary>

The tag can be moved to a different image at any time; the digest always refers to the same content. With both, Docker
uses the digest and the tag is documentation (lesson 082).

</details>

**5. Name three ways a secret can end up in an image, and how to read each one back.**

<details><summary>Answer</summary>

`ARG` used in a `RUN` step (`docker history --no-trunc`), `ENV` (`docker image inspect`, `.Config.Env`), a copied file
deleted in a later layer (`docker save` and the layer's tar file) (lesson 083).

</details>

**6. A secret was pushed in an image last week. You fix the Dockerfile and push a new image. Is the problem solved?**

<details><summary>Answer</summary>

No. Every copy of the old image (registries, caches, laptops, CI machines) still contains it. The secret must be
revoked and rotated (lesson 083).

</details>

**7. nginx fails with `Read-only file system` under `--read-only`. How do you find all the paths it needs?**

<details><summary>Answer</summary>

Run it once normally and list its changes with `docker diff`, then give those paths `--tmpfs` (scratch) or volumes
(data to keep) (lesson 084).

</details>

**8. What does `--cap-drop ALL --cap-add CHOWN` do, and why is it better than the default?**

<details><summary>Answer</summary>

It removes all 14 default capabilities and adds back only `CHOWN`. An attacker inside gets only what the application
needs, not `KILL`, `NET_RAW`, `MKNOD`, `DAC_OVERRIDE` and the rest (lesson 085).

</details>

**9. How does `--pids-limit` protect the other containers on a host?**

<details><summary>Answer</summary>

It bounds the number of processes in the container's cgroup. A fork bomb or runaway process creation fails inside that
container (`can't fork`) instead of filling the host's process table (lesson 086).

</details>

## Practical task

Run the `nginx:1.30-alpine` image as hardened as possible while it still serves its welcome page on host port 8090:
read-only root file system, all capabilities dropped except the ones it needs, no privilege escalation, a process limit
and a memory limit. Prove it serves the page and show its security settings with `docker inspect`.

<details><summary>Solution</summary>

<!-- test: contains=started hardened -->
```bash
docker run -d --name hardened --read-only --tmpfs /var/cache/nginx --tmpfs /run \
  --cap-drop ALL --cap-add CHOWN --cap-add SETUID --cap-add SETGID --security-opt no-new-privileges \
  --pids-limit 100 --memory 128m -p 8090:80 nginx:1.30-alpine > /dev/null && echo "started hardened"
```

<!-- test: retry=10; contains=Welcome to nginx -->
```bash
curl -s http://localhost:8090/ | grep -o '<title>.*</title>'
```

<!-- test: contains=readonly=true; contains=no-new-privileges; output -->
```bash
docker inspect --format 'readonly={{.HostConfig.ReadonlyRootfs}} privileged={{.HostConfig.Privileged}} capdrop={{.HostConfig.CapDrop}} capadd={{.HostConfig.CapAdd}} secopt={{.HostConfig.SecurityOpt}} pids={{.HostConfig.PidsLimit}} memory={{.HostConfig.Memory}}' hardened
```

```text
readonly=true privileged=false capdrop=[ALL] capadd=[CAP_CHOWN CAP_SETGID CAP_SETUID] secopt=[no-new-privileges] pids=100 memory=134217728
```

</details>

## Troubleshooting task

A teammate's image leaks its database password. Reproduce it:

<!-- test: contains=leaky:1.0 -->
```bash
mkdir -p ~/docker-practice/assessment-12 && cd ~/docker-practice/assessment-12
printf 'FROM alpine:3.23\nENV DB_PASSWORD=example-password-change-me\nCMD ["sh", "-c", "echo connecting with $DB_PASSWORD"]\n' > Dockerfile
docker build -q -t leaky:1.0 . > /dev/null && docker image ls leaky --format '{{.Repository}}:{{.Tag}}'
```

Show how anyone with the image reads the password, fix the Dockerfile so the image contains no password but the
application still receives one at run time, and prove both.

<details><summary>Solution</summary>

The password is in the image configuration:

<!-- test: contains=DB_PASSWORD=example-password-change-me; output -->
```bash
docker image inspect --format '{{.Config.Env}}' leaky:1.0
```

```text
[PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin DB_PASSWORD=example-password-change-me]
```

Remove the `ENV` line; give the value when the container starts, from a file:

<!-- test: contains=image clean; contains=connecting with example-password-change-me; output -->
```bash
printf 'FROM alpine:3.23\nCMD ["sh", "-c", "echo connecting with $DB_PASSWORD"]\n' > Dockerfile
docker build -q -t leaky:1.1 . > /dev/null
docker image inspect --format '{{.Config.Env}}' leaky:1.1 | grep -q DB_PASSWORD || echo "image clean"
printf 'DB_PASSWORD=example-password-change-me\n' > db.env
docker run --rm --env-file db.env leaky:1.1
```

```text
image clean
connecting with example-password-change-me
```

Then rotate the password: `leaky:1.0` may already have been pulled elsewhere.

</details>

## Real-world scenario

A security audit of your company's Docker hosts finds containers running as root, three containers started with
`--privileged` "because the monitoring agent needed it", no memory limits anywhere, and base images that were last
rebuilt eight months ago. You have one sprint. What do you do first, and how do you keep it from coming back?

<details><summary>Model answer</summary>

Order by risk. First the `--privileged` containers: find out which device or capability the monitoring agent really
needs (often read-only mounts of `/proc` and `/sys`, or one capability) and replace `--privileged` with exactly that
(lessons 080, 085). Then rebuild every image on current base images and scan them, because old bases carry known
CVEs with available fixes (lesson 082). Then add memory, CPU and pids limits based on measured usage (lesson 086), and
switch images to non-root users, starting with internet-facing services (lesson 081). To keep it fixed: scan and
rebuild images in CI on a schedule, pin bases by digest with automated update pull requests, and enforce the rules at
deployment (an audit script with `docker inspect`, or Kubernetes Pod Security Standards / admission policies).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f hardened > /dev/null 2>&1 || true
docker image rm -f leaky:1.0 leaky:1.1 > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/assessment-12
```
