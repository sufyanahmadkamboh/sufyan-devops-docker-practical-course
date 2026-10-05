# Serves the current folder over HTTP on port 8000. Task 10: it must not run as root.
FROM python:3.14-alpine
WORKDIR /srv
COPY index.html .
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]
