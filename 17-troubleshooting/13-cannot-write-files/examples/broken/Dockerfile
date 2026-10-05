FROM python:3.14-slim
RUN groupadd --system app && useradd --system --gid app --uid 10001 app
WORKDIR /app
COPY app.py ./
RUN mkdir data
USER app
EXPOSE 8080
CMD ["python", "app.py"]
