# Docker Practical Course · from beginner to advanced

[![test-lessons](https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course/actions/workflows/test.yml/badge.svg)](https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course/actions/workflows/test.yml)

A hands-on Docker course in 22 modules: 116 lessons, 25 troubleshooting problems, 8 projects, a capstone and a
final exam. Every command in it is run by CI on a fresh Docker engine, and every output you see is the real output of
that command.

You do not just read about containers here. In every lesson you run something, look inside it, **break it on
purpose**, read the real error, find the cause and fix it, because that is what working with Docker in a team is.

## What is Docker?

Docker packages an application together with everything it needs to run (the runtime, the libraries, the system
dependencies and the default configuration) into an **image**. An image runs as a **container**: an isolated process
that behaves the same on a laptop, in CI and on a production server. Images are built from a `Dockerfile`, stored in
a **registry**, and run by the Docker engine, or by Kubernetes, which runs the very same images at scale.

## Why this course?

- **Practical first.** Each concept follows the same loop:
  *understand → visualize → implement → run → inspect → break → troubleshoot → fix → improve → practice → real world.*
- **Errors are part of the lesson.** Every lesson has a *Break it* section with the real error message, and the
  investigation that leads to the fix. Module 17 is 25 production-style problems, each worked through from symptom
  to prevention.
- **Real applications.** Node.js, Python, Go, Java and PHP applications, Nginx, PostgreSQL and Redis: containerized,
  connected, persisted, secured, measured and shipped.
- **Tested.** [tests/run.sh](tests/run.sh) runs every lesson exactly as you would type it; the
  [CI workflow](.github/workflows/test.yml) runs the whole course every week.

## Who is it for?

- Developers who want to package and run their applications with Docker, and understand what happens underneath.
- Beginners in DevOps, platform and cloud engineering: Docker is the base of CI/CD pipelines and Kubernetes.
- Engineers who already use Docker and want to troubleshoot, secure and optimize it with confidence.

## Prerequisites

- Basic terminal use: `cd`, `ls`, running a command, editing a file.
- A computer with 8 GB of RAM (16 GB recommended) and about 15 GB of free disk space.
- **Windows:** Docker Desktop (WSL 2 backend) and [Git for Windows](https://git-scm.com/download/win), whose
  **Git Bash** runs every command of the course. **macOS:** Docker Desktop and the Terminal. **Linux:** Docker Engine.
- No Docker knowledge. Module 01 starts from zero, and [lesson 005](01-fundamentals/005-installing-docker/README.md)
  covers the installation.

## Course map

| Module | Level | You learn |
|---|---|---|
| [01 · Fundamentals](01-fundamentals/README.md) | beginner | what Docker is, containers vs VMs, architecture, installation |
| [02 · Containers](02-containers/README.md) | beginner | run, list, stop, start, remove, name; Nginx, ports, logs, exec, inspect |
| [03 · Images](03-images/README.md) | beginner | layers, pull, list, remove, tags, why `latest` is dangerous |
| [04 · Dockerfiles](04-dockerfiles/README.md) | beginner | `FROM` `WORKDIR` `COPY` `RUN` `CMD` `ENTRYPOINT` `ENV` `ARG` `EXPOSE` `USER` |
| [05 · Builds](05-builds/README.md) | intermediate | build context, `.dockerignore`, layers and the build cache |
| [06 · Containerizing applications](06-application-containerization/README.md) | intermediate | Node.js, Python, Go, Java, PHP-FPM + Nginx, compared |
| [07 · Networking](07-networking/README.md) | intermediate | bridge networks, custom networks, DNS, `EXPOSE` vs `-p`, troubleshooting |
| [08 · Storage](08-storage/README.md) | intermediate | writable layer, bind mounts, volumes, a persistent database |
| [09 · Environment configuration](09-environment-config/README.md) | intermediate | `-e`, `--env-file`, configuration vs secrets |
| [10 · Docker Compose](10-compose/README.md) | intermediate | multi-container applications: services, networks, volumes, healthchecks, profiles |
| [11 · Registries](11-registry/README.md) | intermediate | Docker Hub, image naming, private registries, GHCR |
| [12 · Security](12-security/README.md) | advanced | non-root, minimal images, leaked secrets, read-only, capabilities, limits |
| [13 · Multi-stage builds](13-multistage/README.md) | advanced | small, safe production images for Node.js, Go and Java, measured |
| [14 · Observability](14-observability/README.md) | advanced | healthchecks, logs, stats, events |
| [15 · Resources](15-resources/README.md) | advanced | CPU and memory limits, out-of-memory kills |
| [16 · Advanced](16-advanced/README.md) | advanced | metadata, labels, logging drivers, Buildx, multi-architecture images, cache |
| [17 · Troubleshooting](17-troubleshooting/README.md) | all levels | 25 real problems: symptoms → investigation → root cause → fix → prevention |
| [18 · Production](18-production/README.md) | advanced | production Dockerfiles, container design, immutability, configuration, review |
| [19 · Docker in CI/CD](19-ci-cd/README.md) | advanced | build, test, scan and push images in a pipeline |
| [20 · Docker and Kubernetes](20-kubernetes/README.md) | advanced | run an image built in this course on a Kubernetes cluster |
| [21 · Projects](21-projects/README.md) | practice | 8 projects, from a static site to a multi-stack application |
| [22 · Capstone](22-capstone/README.md) | final | a production-style stack, and the [final exam](22-capstone/final-exam/README.md) |

Also: the [command reference](docs/command-reference.md), every command of the course with the lesson that teaches
it, and the [diagrams](diagrams/).

## How a lesson works

Every lesson folder has the full lesson in `README.md`, plus the same content split for practice:

| File | Contents |
|---|---|
| `README.md` | what, visual, lab setup, demonstration, command breakdown, lab, break it, troubleshoot it, fix it, challenge, real-world example, recap, cleanup |
| `lab.md` | the hands-on lab: instructions, expected result, verification |
| `challenge.md` / `solution.md` | the practice challenge, and its solution in a separate file |
| `troubleshooting.md` | the intentional failure, its investigation and the fix |
| `commands.md` | every command of the lesson, in order |
| `examples/` | the files the lesson uses: `before/`, `broken/`, `fixed/`, `final/` where useful |

Every module ends with an **assessment**: a knowledge check, a practical task, a troubleshooting task and a real-world
scenario.

## Setup

```bash
git clone https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course.git docker-practical-course
cd docker-practical-course
docker version
bash scripts/prefetch-images.sh
```

`prefetch-images.sh` downloads the 18 images the course uses, once. Docker Hub limits anonymous downloads;
if it answers `toomanyrequests`, run `bash scripts/prefetch-images.sh --mirror` (it uses Google's public mirror of the
official images; [troubleshooting problem 25](17-troubleshooting/README.md) explains the limit).

Run every command **from the course folder** in Git Bash (Windows), Terminal (macOS) or a Linux shell.

## Running and resetting the labs

Lessons that need files create a fresh practice folder outside the course with
[scripts/lab.sh](scripts/lab.sh), so the course itself never changes:

```bash
bash scripts/lab.sh lesson-041 examples/python-api     # creates ~/docker-practice/lesson-041
cd ~/docker-practice/lesson-041
```

Running the same `lab.sh` line again **resets** the lab: the folder is replaced with a clean copy. Each lesson's
*Cleanup* section removes the containers, images, networks and volumes it created. Every lesson starts in the course
folder: after a lab, `cd` back to where you cloned the course before you start the next lesson.

## When something does not work

1. Read the last line of the error: Docker almost always says what went wrong.
2. Look at the state: `docker ps -a`, `docker logs NAME`, `docker inspect NAME`.
3. Compare with the lesson's *Troubleshoot it* section, then with [module 17](17-troubleshooting/README.md), which is
   organized by symptom (exits immediately, not reachable, permission denied, out of memory, …).
4. Start clean: run the lesson's *Cleanup*, then its *Lab setup* again.

## Projects and capstone

The [8 projects](21-projects/README.md) apply the course to complete applications: a static site, Node.js, Python,
Go and Java APIs, a database container, a full-stack Compose application and a multi-stack application. The
[capstone](22-capstone/README.md) brings everything together in one production-style stack (Nginx reverse proxy,
frontend, API, PostgreSQL, persistent volume) with multi-stage builds, a custom network, configuration and secrets,
healthchecks, resource limits, logging, security hardening, Compose, a registry and a CI pipeline. The
[final exam](22-capstone/final-exam/README.md) checks the skills one by one.

## Cleanup

Each lesson cleans up after itself. To remove everything the course created at once (containers, networks and volumes
of this computer's engine, and the practice folders):

```bash
docker container rm -f $(docker container ls -aq) 2> /dev/null
docker network prune -f && docker volume prune -af
rm -rf ~/docker-practice
```

> These commands remove **all** containers and unused volumes on this engine, not only the course's. Run them only on
> a computer where nothing else uses Docker. `docker image prune -a` also removes the downloaded images.

## Videos

A 21-video series (5 h 27 min) follows the course: one video per module, the 25 troubleshooting problems and the
capstone. Each lesson becomes a short conversation between a senior and a junior engineer over the lesson's diagram, its
real commands and outputs, the mistake made on purpose and the fix. Every video exists in two versions with identical
pictures: full (narration, music, sound effects) and silent. The videos are generated from the lessons by
[video/build.py](video/build.py); it also writes the titles, descriptions, chapters and captions (kept locally, not in the repository),
and every audio asset is listed in [video/AUDIO-LICENSES.md](video/AUDIO-LICENSES.md).

## Docker, CI/CD and Kubernetes

Docker is where the delivery chain starts. A CI pipeline builds the image from the `Dockerfile`, tests and scans it,
and pushes it to a registry ([module 19](19-ci-cd/README.md)); Kubernetes pulls that same image and runs it as Pods
([module 20](20-kubernetes/README.md)). Everything you learn here (images, ports, environment, volumes, healthchecks,
resource limits, non-root users) maps directly onto Kubernetes objects.

Related courses: [Git Practical Course](https://github.com/sufyanahmadkamboh/sufyan-devops-git-practical-course) ·
[Kubernetes from zero](https://github.com/sufyanahmadkamboh/sufyan-devops-kubernetes-from-zero) ·
[Secure supply chain (signed images in CI)](https://github.com/sufyanahmadkamboh/sufyan-devops-secure-supply-chain).

## Repository structure

```text
docker-practical-course/
├── 01-fundamentals … 16-advanced     lessons 001–105, an assessment per module
├── 17-troubleshooting                25 problems, organized by symptom
├── 18-production … 20-kubernetes     lessons 130–140
├── 21-projects                       8 projects
├── 22-capstone                       the capstone and the final exam
├── examples/                         the applications the lessons containerize
├── scripts/                          prefetch-images.sh, lab.sh
├── diagrams/                         the course diagrams
├── docs/                             command reference, glossary, interview questions, authoring guide
├── study/                            the study guide (PDF)
├── tests/                            the lesson runner used locally and in CI
└── video/                            the video series (scripts and build)
```

## Testing the course

```bash
bash tests/run.sh 02-containers/*/README.md        # run lessons exactly as written, in a sandbox
```

The runner gives each lesson a fresh `HOME` and Docker CLI configuration, starts and ends every lesson with an empty
engine (images stay cached) and checks every block's output. [docs/AUTHORING.md](docs/AUTHORING.md) describes the
lesson format.

## License

[MIT](LICENSE)
