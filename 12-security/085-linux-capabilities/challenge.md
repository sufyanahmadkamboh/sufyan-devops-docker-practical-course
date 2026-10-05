<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 085 · Linux capabilities · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

The Python web server from lesson 084 runs as root on port 8081. Find the smallest set of capabilities it needs: start
it with `--cap-drop ALL` and check that it still answers. Then show which capabilities the server process actually has
while it runs.

The solution is in [solution.md](solution.md).
