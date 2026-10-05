FROM eclipse-temurin:25-jdk-alpine
WORKDIR /app
COPY src ./src
# compile and package into an executable jar (a Maven or Gradle build does the same, lesson 090)
RUN javac -d classes src/Main.java \
 && jar --create --file app.jar --main-class Main -C classes . \
 && rm -rf classes
RUN addgroup -S app && adduser -S -G app app
USER app
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
