FROM python:3.14-slim
RUN groupadd --system --gid 10001 web && useradd --system --uid 10001 --gid web --no-create-home web
WORKDIR /app
# the content stays owned by root: the server can read it, not change it
COPY public/ public/
EXPOSE 8080
USER 10001:10001
CMD ["python", "-m", "http.server", "8080", "--directory", "public"]
