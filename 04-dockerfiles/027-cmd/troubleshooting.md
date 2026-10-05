<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 027 · CMD · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague writes the exec form with single quotes, as in Python:

```bash
printf "FROM alpine:3.23\nCMD ['echo', 'hello']\n" > Dockerfile.quotes
docker build -q -f Dockerfile.quotes -t cmd-form:quotes . > /dev/null
docker run --rm cmd-form:quotes
```

```text
/bin/sh: [echo,: not found
```

## Troubleshoot it

The build worked, the container fails with exit status 127 ("command not found"), and the "command" it tried is
`[echo,`. Look at what Docker stored:

```bash
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:quotes
```

```text
["/bin/sh","-c","['echo', 'hello']"]
```

Single quotes are not valid JSON, so Docker did not recognise an exec-form array and treated the whole line as a
**shell-form** command. The shell then split it into words and tried to run a program called `[echo,`. The build
checker spots this without building:

```bash
docker build --check -f Dockerfile.quotes . 2>&1 | grep -A1 WARNING
```

## Fix it

Use double quotes, as JSON requires:

```bash
printf 'FROM alpine:3.23\nCMD ["echo", "hello"]\n' > Dockerfile.quotes
docker build -q -f Dockerfile.quotes -t cmd-form:quotes . > /dev/null
docker run --rm cmd-form:quotes
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:quotes
```

```text
hello
["echo","hello"]
```
