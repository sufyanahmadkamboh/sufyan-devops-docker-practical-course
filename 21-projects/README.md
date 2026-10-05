# Module 21 · Projects

> 8 projects · about 9 hours · run every command from the course folder

Each project applies the course to one complete application. It states a goal and a requirements checklist, shows the
architecture, builds the solution step by step, **verifies every requirement with a command**, and breaks one thing
the way it breaks in real teams. The finished files are in each project's `solution/` folder: try to write your own
first, then compare.

| # | Project | Skills | Time |
|---|---|---|---|
| 01 | [Static website on Nginx](01-static-site/README.md) | custom `nginx.conf`, non-root, `HEALTHCHECK`, `--read-only` + `--tmpfs` | 45 min |
| 02 | [Production Node.js API](02-node-api/README.md) | `npm ci`, multi-stage, non-root, exec-form `CMD`, graceful `SIGTERM` | 1 h |
| 03 | [Python API with Redis](03-python-api/README.md) | Gunicorn, Compose, service DNS, `depends_on` + healthchecks, named volume | 1 h |
| 04 | [Go API, as small as it gets](04-go-api/README.md) | static binaries, distroless vs `scratch`, measured sizes, shell vs exec form | 45 min |
| 05 | [Java API on a JRE](05-java-api/README.md) | JDK → JRE multi-stage, executable jars, container-aware heap | 1 h |
| 06 | [A database container you can back up](06-database-container/README.md) | init scripts, volumes, `pg_dump` / `pg_restore`, restore tests | 1 h |
| 07 | [Full-stack application with Compose](07-full-stack-compose/README.md) | three tiers, internal network, `.env` configuration, credential changes | 1.5 h |
| 08 | [Four stacks behind one proxy](08-multi-stack/README.md) | path routing, four languages, limits, failure isolation, `nginx -s reload` | 2 h |

Every project starts from a clean lab (`bash scripts/lab.sh project-NN …`) and ends with a *Cleanup* section that
removes its containers, images, networks and volumes.

Next: [Capstone](../22-capstone/README.md)
