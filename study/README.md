# How to use this study guide

This guide is the revision companion to the course. Every lesson is condensed to what it teaches, its diagram, its
command table and its recap. The full lessons, with every command, its real output, the labs, the challenges and
their solutions, live in the repository: each summary links to its lesson.

## How to study

1. **Do the lesson first, read the summary afterwards.** Docker is learned with your hands: run every command of a
   lesson, break it the way the *Break it* section does, and read the real error before you read the explanation.
2. **Read the error's last line.** Almost every Docker error says what went wrong: `port is already allocated`,
   `executable file not found`, `Read-only file system`, `401 Unauthorized`. The course teaches you to trust it.
3. **Look before you fix.** `docker ps -a`, `docker logs`, `docker inspect`, `docker exec`: the four commands that
   answer most questions. Troubleshooting problems 01–25 practise them in the order you would use them.
4. **End every module with its assessment**: a knowledge check, a practical task, a troubleshooting task and a
   real-world scenario. Redo the tasks you could not do without the answer.
5. **Finish with the capstone and the final exam.** The exam grades 13 tasks against the real state of your engine.

## A study plan

| Week | Modules | Goal |
|---|---|---|
| 1 | 01–04 | run, inspect and remove containers; read images; write Dockerfiles |
| 2 | 05–09 | fast builds; containerize five stacks; networks, storage and configuration |
| 3 | 10–13 | multi-container applications with Compose; registries; security; multi-stage builds |
| 4 | 14–17 | healthchecks, logs, limits, Buildx; the 25 troubleshooting problems |
| 5 | 18–22 | production practice, CI/CD, Kubernetes; projects, capstone and final exam |

One hour a day is enough: a lesson takes 15–30 minutes, plus its challenge.
