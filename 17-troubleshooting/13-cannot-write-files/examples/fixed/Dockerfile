FROM python:3.14-slim
RUN groupadd --system app && useradd --system --gid app --uid 10001 app
WORKDIR /app
COPY app.py ./
# the one directory the application writes to belongs to its user; the code stays owned by root
RUN mkdir data && chown app:app data
VOLUME /app/data
USER app
EXPOSE 8080
CMD ["python", "app.py"]
