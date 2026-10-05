<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 013 · Running multiple containers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Start five Nginx containers in a loop, `web-1` … `web-5`, on ports 8091–8095 with the label `project=load-test`, then
prove that every one of them answers, and remove the whole group with one command.

## Solution

```bash
for i in 1 2 3 4 5; do
  docker run -d --name "web-$i" --label project=load-test -p "809$i:80" nginx:1.30-alpine > /dev/null
done
```

```bash
ok=0
for i in 1 2 3 4 5; do curl -sf "http://localhost:809$i" > /dev/null && ok=$((ok + 1)); done
echo "$ok of 5 answered"
```

```text
5 of 5 answered
```

```bash
echo "removed: $(docker rm -f $(docker ps -aq --filter label=project=load-test) | wc -l | tr -d ' ')"
```
