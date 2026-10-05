<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 026 · RUN · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

`/bin/sh -c` only reports the exit status of the **last** command of a pipeline. Show that this step passes although
its first command fails, then make it fail correctly:

```text
RUN false | echo "pipeline finished"
```

The solution is in [solution.md](solution.md).
