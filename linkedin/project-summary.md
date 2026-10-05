# Docker Practical Course · project summary

**What:** a free, hands-on Docker course from beginner to advanced: 116 lessons from the first container to
Dockerfiles, builds, networking, storage, configuration, Compose, registries, security, multi-stage builds,
observability, resource limits, Buildx and multi-architecture images, production practice, CI/CD and Kubernetes;
25 troubleshooting problems, 8 projects, a capstone and a final exam.

**Problem:** Docker is usually learned as a handful of commands; the hard parts at work are the failures: ports,
networks and DNS, permissions, lost data, out-of-memory kills, unhealthy services, slow and huge builds, leaked
secrets and registry errors. Those are rarely practised.

**Contents**
- 116 lessons, each: concept, ASCII diagram, lab, real commands and outputs, command table, hands-on lab with expected
  result and verification, a failure made on purpose, troubleshooting, fix, practice challenge with a separate
  solution, real-world example and recap; generated `lab.md`, `challenge.md`, `solution.md`, `troubleshooting.md` and
  `commands.md` per lesson
- an assessment per module (knowledge check, practical task, troubleshooting task, real-world scenario), a command
  reference generated from the lessons and linked to them, a labs index and a troubleshooting index
- 25 troubleshooting problems in the format problem → symptoms → investigation → commands → output interpretation →
  root cause → fix → verification → prevention
- 8 projects: static site, Node.js API, Python API with Redis, Go API (single-stage vs distroless vs scratch), Java API
  (JDK → JRE), a database container with backup and restore, a full-stack Compose application, a multi-stack proxy
- a capstone: Nginx reverse proxy, frontend, Go API (pgx) and PostgreSQL 18 with multi-stage builds, edge and internal
  networks, environment configuration, a secret file, healthchecks, resource limits, log rotation, non-root users,
  read-only file systems, dropped capabilities, a local registry and deployment by digest; a GitHub Actions workflow
  builds, smoke-tests and pushes the images to GHCR with the workflow token
- a final exam of 13 tasks on a prepared, partly broken environment, graded by a script, with a separate solution
- a 21-video series (full and silent versions), a 152-page study guide PDF, 12 diagrams, a glossary and 28
  interview questions

**Engineering details**
- `tests/mdrun.py` runs every Bash block as a learner types it and writes the real outputs back into the lessons; a
  sandbox (temporary HOME, separate Docker CLI configuration and kubeconfig, a copy of the course) keeps the author's
  environment untouched; every lesson starts and ends with an empty engine; a lock serialises runs on one engine
- GitHub Actions runs all 1,777 blocks in four parallel groups on Docker Engine 29 with current Compose and Buildx,
  a Docker Hub pull-through mirror, the containerd image store, QEMU for arm64 and kind for Kubernetes; static checks
  for links, generated files and ShellCheck
- the lessons were written on Docker Desktop and corrected where a Linux engine behaves differently (root-owned files
  from bind mounts, DNS search domains, fast-failing lookups, credential helpers, OOM events), with both behaviours
  explained
- the videos are generated from the lessons: scenes per lesson, two narrator voices, real recorded outputs, original
  synthesised music and effects, captions, chapters and an audio-license register with timestamps

**Repository:** https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course
