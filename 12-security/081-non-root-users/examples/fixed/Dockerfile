FROM python:3.14-alpine
RUN addgroup -S app && adduser -S -G app -H app
WORKDIR /app
COPY app.py .
# the only folder the application writes to belongs to its user; the code stays owned by root (read-only for app)
RUN mkdir data && chown app:app data
USER app
EXPOSE 8080
CMD ["python", "app.py"]
