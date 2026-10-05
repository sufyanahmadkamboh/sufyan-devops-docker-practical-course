FROM python:3.14-alpine
WORKDIR /app
COPY app.py .
USER nobody
EXPOSE 8080
# healthy = /health answers within 2 seconds
HEALTHCHECK --interval=2s --timeout=3s --start-period=2s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)" || exit 1
CMD ["python", "app.py"]
