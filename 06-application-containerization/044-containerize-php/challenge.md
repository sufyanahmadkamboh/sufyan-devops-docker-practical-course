<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 044 · Containerizing a PHP application · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Static files should be served by Nginx without touching PHP. Create `public/robots.txt`, give the Nginx container
read-only access to `public/` at the path its `root` points to (`/var/www/html/public`), and show that `/robots.txt`
comes back as `text/plain` from Nginx while `/` still comes from PHP.

The solution is in [solution.md](solution.md).
