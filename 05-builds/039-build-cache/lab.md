<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 039 · The build cache · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** With the well-ordered `Dockerfile`, add a new dependency line to `requirements.txt`
(`itsdangerous==2.2.0`, which Flask already uses) and rebuild. Which steps run?

**Expected result.** `COPY requirements.txt`, `RUN pip install` and `COPY . .` run again (the input of step 3 changed,
so everything after it is invalid); `WORKDIR` stays cached. The second `grep -A1` shows the `pip` step and the line
after it: no `CACHED`.

**Verification.**

```bash
cd ~/docker-practice/lesson-039
echo "itsdangerous==2.2.0" >> requirements.txt
docker build -t cache-api:3 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```
