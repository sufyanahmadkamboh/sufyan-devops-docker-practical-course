# syntax=docker/dockerfile:1
# Stage 1: compile and package with the full JDK.
FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /src
COPY src/ src/
RUN javac -d out src/Main.java \
 && jar --create --file app.jar --main-class Main -C out .

# Stage 2: run the jar on the JRE only (no compiler), as an unprivileged user.
FROM eclipse-temurin:25-jre-alpine
RUN addgroup -S app && adduser -S -G app -u 10001 app
WORKDIR /app
COPY --from=build /src/app.jar .
USER app
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
  CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/health"]
# size the heap from the container's memory limit, not from the host's memory
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
