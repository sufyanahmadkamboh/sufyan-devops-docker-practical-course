# Final exam

> ⏱ 2 hours · 13 tasks · run every command from the course folder · pass mark: 13/13, every task is graded by a
> script against the real state of your engine

The exam prepares a set of containers and files, several of them broken, the way you would find a system you have just
inherited. Investigate, fix and build, using only what the course taught. The [solution](SOLUTION.md) is for
instructors (and for you, **after** your attempt).

## Start

<!-- test: contains=exam ready -->
```bash
bash 22-capstone/final-exam/start-exam.sh
```

Everything you need is in `~/docker-practice/exam`. Running `start-exam.sh` again resets the exam. Check your progress
at any time:

<!-- test: fail; contains=score: 0/13 -->
```bash
bash 22-capstone/final-exam/check-exam.sh
```

Answers to tasks 1–4 and 6 go into `~/docker-practice/exam/answers.txt`, one `key=value` per line, for example
`web_port=1234`.

## Tasks

| # | Skill | Task |
|---|---|---|
| 1 | inspect containers | Which image does `exam-web` run, and on which **host** port is it published? Answer `web_image=` (with its tag) and `web_port=`. |
| 2 | inspect images | What is the entrypoint of the image `redis:8-alpine`? Answer `redis_entrypoint=`. |
| 3 | why a container exits | `exam-worker` is not running. With which exit code did it stop, and why? Answer `worker_exit_code=`. |
| 4 | logs | `exam-api` runs, but something is wrong. Which file can it not open? Answer `api_error_file=`. |
| 5 | networking | `exam-client` must reach `exam-cache`. Fix it without recreating either container. |
| 6 | connectivity | Prove it: from `exam-client`, send `PING` to `exam-cache` on port 6379 (the image has `nc`) and record the reply as `cache_reply=`. |
| 7 | volumes | `exam-notes` keeps `/data/note.txt` in its writable layer, so the note dies with the container. Recreate `exam-notes` (same name, same image) so that `/data` is the named volume `exam-notes-data` and still contains a `note.txt` with the text `remember the milk`. |
| 8 | environment variables | `exam-greeter` (image `exam-greeter:1.0`) stops right after starting. Find out why and run it again, same name, so it keeps running. |
| 9 | optimize a Dockerfile | `~/docker-practice/exam/optimize` builds a working but huge image. Change its Dockerfile so that `exam-optimized:1.0` is **under 30 MB** and still answers on `/health` (port 8080). |
| 10 | remove privileges | `~/docker-practice/exam/rootapp` runs as root. Build `exam-nonroot:1.0` from it so the server runs as a non-root user and still serves its page on port 8000. |
| 11 | Compose deployment | In `~/docker-practice/exam/compose`, write a `compose.yaml` that runs the API (built from the Dockerfile there) and `redis:8-alpine`; the API must answer on `http://localhost:8091/visits`. Start it with the project name `exam`. |
| 12 | verify health | Every service of the `exam` project must report **healthy** (add healthchecks; the API has `/health`). |
| 13 | registry | Run a registry on `localhost:5000` and push `exam-optimized:1.0` to it as `localhost:5000/exam/optimized:1.0`. |

## Grade

<!-- test: skip -->
```bash
bash ~/docker-practice/exam/check-exam.sh        # a copy of 22-capstone/final-exam/check-exam.sh
```

```text
PASS  task  1  inspect a container: image and host port of exam-web
…
score: 13/13
```

## Cleanup

<!-- test -->
```bash
docker rm -f exam-web exam-worker exam-api exam-cache exam-client exam-notes exam-greeter exam-registry > /dev/null 2>&1 || true
(cd ~/docker-practice/exam/compose && docker compose -p exam down -v --rmi local > /dev/null 2>&1) || true
docker network rm exam-front exam-back > /dev/null 2>&1 || true
docker volume rm exam-notes-data > /dev/null 2>&1 || true
docker image rm -f exam-greeter:1.0 exam-optimized:1.0 exam-nonroot:1.0 localhost:5000/exam/optimized:1.0 > /dev/null 2>&1 || true
rm -rf ~/docker-practice/exam
echo "exam removed"
```
