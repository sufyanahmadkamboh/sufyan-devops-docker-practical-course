<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 058 · A persistent database · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Back up the `orders` table's database with `pg_dump` into `backup.sql` on your computer, delete the table, and restore
it from the backup.

## Solution

```bash
cd ~/docker-practice/lesson-058
docker exec db pg_dump -U postgres postgres > backup.sql
docker exec db psql -U postgres -c "DROP TABLE orders" > /dev/null
docker exec -i db psql -U postgres -q < backup.sql > /dev/null
echo "restored: $(docker exec db psql -U postgres -tAc 'SELECT count(*) FROM orders') orders"
```

```text
restored: 2 orders
```

`docker exec -i` passes your terminal's input (here the file) into the container. A volume protects against losing the
container; only backups protect against deleting the data, a broken disk or a bad migration.
