Most Docker tutorials stop at "docker run". Then real work begins: a port that is already allocated, a container that exits with 137 at 3 a.m., a service that is "Up" but unhealthy, an image that only works on the laptop it was built on. So I built a free, hands-on Docker course that teaches exactly those moments. 🐳👇

Think of a container as a shipping container for software: the same box runs on any ship. Every lesson packs one, ships it, then breaks it on purpose so you learn to read the error when the cargo does not arrive.

That is the "Docker Practical Course: Docker From Beginner to Advanced":

📚 116 lessons, from your first container to Dockerfiles, builds and the cache, networking, storage, Compose, registries, security, multi-stage builds, observability, resource limits, Buildx and multi-architecture images
🧯 25 troubleshooting problems: Problem → Symptoms → Investigation → Root cause → Fix → Verification → Prevention
🏗️ 8 projects (Node.js, Python, Go, Java, PHP, a database, full-stack Compose, a multi-stack proxy) and a capstone: an Nginx proxy, frontend, Go API and PostgreSQL, hardened, health-checked, limited, pushed by digest and built in CI
☸️ the bridge to CI/CD and Kubernetes: the same image built in a pipeline and deployed to a cluster

Every concept follows the same loop: Understand → Visualize → Implement → Run → Inspect → Break → Troubleshoot → Fix → Improve → Practice → Real world.

Things I learned while building and testing it:
🔹 the same Go API image measured 98.0 MB single-stage, 3.3 MB on distroless and 2.5 MB on scratch
🔹 a bind-mounted container that runs as root leaves root-owned files in your folder on Linux; Docker Desktop hides it
🔹 a cloud server's DNS search domain makes BusyBox "nslookup web" fail while the application resolves "web" fine
🔹 PostgreSQL 18 refuses to start when a volume is mounted at the old /var/lib/postgresql/data path, and says so clearly
🔹 running is not healthy: a HEALTHCHECK turns "Up" into "unhealthy", and Compose can wait for "healthy" before it starts the next service

✅ Every lesson is also a test: 1,777 code blocks run automatically in GitHub Actions on a fresh Docker 29 engine, in a sandbox, and the outputs in the lessons are the real outputs. The course also runs on Docker Desktop.

Also included: an assessment per module, a command reference linked to the lessons, a final exam with an automatic grader and a separate solution, a 21-video series (5 h 27 min in total, full and silent versions), a 152-page study guide PDF, a glossary and 28 interview questions.

🔗 Repository: https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course
🌐 All my projects: https://sufyanahmadkamboh.github.io/

Which Docker error cost you the most time? 💬

#Docker #DevOps #Containers #DockerCompose #Kubernetes #CloudNative #PlatformEngineering #LearningDevOps #OpenSource
