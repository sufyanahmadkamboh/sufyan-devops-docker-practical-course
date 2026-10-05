<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 048 · Custom networks · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show the subnet and gateway of `backend-net`, and the names of the containers attached to it.

**Expected result.** Subnet `172.30.2.0/24`, a gateway in it, and the containers `db` and `api`.

**Verification.**

```bash
docker network inspect backend-net --format '{{(index .IPAM.Config 0).Subnet}} via {{(index .IPAM.Config 0).Gateway}}'
docker network inspect backend-net --format '{{range .Containers}}{{.Name}} {{end}}'
```
