FROM python:3.14-slim
WORKDIR /app
COPY app.py .
EXPOSE 8080
HEALTHCHECK --interval=2s --timeout=2s --retries=2 CMD curl -fs http://localhost:8080/health || exit 1
CMD ["python", "app.py"]
