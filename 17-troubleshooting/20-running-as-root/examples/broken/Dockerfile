FROM python:3.14-slim
WORKDIR /app
COPY public/ public/
EXPOSE 8080
# no USER instruction: the server runs as root (uid 0)
CMD ["python", "-m", "http.server", "8080", "--directory", "public"]
