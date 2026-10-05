FROM python:3.14-slim
WORKDIR /app
COPY app.py .
EXPOSE 8080
# the image has Python but no curl: check with the tools the image really contains
HEALTHCHECK --interval=2s --timeout=2s --retries=2 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]
CMD ["python", "app.py"]
