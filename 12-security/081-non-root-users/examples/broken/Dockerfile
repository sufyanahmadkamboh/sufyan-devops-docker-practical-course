FROM python:3.14-alpine
WORKDIR /app
COPY app.py .
RUN addgroup -S app && adduser -S -G app -H app
USER app
EXPOSE 8080
CMD ["python", "app.py"]
