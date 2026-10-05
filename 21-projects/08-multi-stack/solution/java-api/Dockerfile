FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /src
COPY src/ src/
RUN javac -d out src/Main.java && jar --create --file app.jar --main-class Main -C out .

FROM eclipse-temurin:25-jre-alpine
RUN adduser -S -u 10001 app
WORKDIR /app
COPY --from=build /src/app.jar .
USER app
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/health"]
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
