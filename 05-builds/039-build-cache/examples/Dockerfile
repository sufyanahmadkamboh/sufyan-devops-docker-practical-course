FROM python:3.14-slim
WORKDIR /app
# dependencies first: this layer is rebuilt only when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# the code last: it changes on every commit
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
