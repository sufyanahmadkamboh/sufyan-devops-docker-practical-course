FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "app:app"]
