FROM python:3.14-slim
RUN groupadd --system app && useradd --system --gid app --uid 10001 app
WORKDIR /app
COPY app.py ./
# owned by root, readable by the app's group, writable by nobody at run time
COPY --chown=root:app --chmod=640 settings.ini ./
USER app
EXPOSE 8080
CMD ["python", "app.py"]
