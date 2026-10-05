# stage 1: the JDK compiles and packages the application
FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /src
COPY src ./src
RUN javac -d classes src/Main.java \
 && jar --create --file app.jar --main-class Main -C classes .

# stage 2: the JRE only runs it
FROM eclipse-temurin:25-jre-alpine
RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --from=build /src/app.jar ./app.jar
USER app
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
