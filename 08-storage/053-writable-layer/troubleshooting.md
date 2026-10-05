<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 053 · The container's writable layer · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Remove the container (as a cleanup job or a redeploy does), then start a "new version" from the same image and look
for the notes:

```bash
docker rm notes > /dev/null
docker run --rm alpine:3.23 cat /data/notes.txt 2>&1
```

```text
cat: can't open '/data/notes.txt': No such file or directory
```

## Troubleshoot it

`No such file or directory`: the new container starts from the image, which never contained `/data/notes.txt`. The
file only existed in the writable layer of `notes`, and `docker rm` deleted that layer. Confirm that no container
holds it any more:

```bash
docker container ls -a --filter name=^notes$ --format '{{.Names}}' | grep -q . || echo "no container named notes"
```

```text
no container named notes
```

Every redeploy (new image version → new container) and every `docker run --rm` loses the writable layer. It is
temporary storage by design.

## Fix it

Store the data outside the container, in a **named volume** (lesson 055), so a new container sees it:

```bash
docker run --rm -v notes-data:/data alpine:3.23 sh -c 'echo "a note" >> /data/notes.txt'
docker run --rm -v notes-data:/data alpine:3.23 cat /data/notes.txt
```

```text
a note
```

Two containers, both removed at once (`--rm`), and the note survived: it lives in the volume `notes-data`.
