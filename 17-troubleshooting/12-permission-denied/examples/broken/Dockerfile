FROM python:3.14-slim
RUN groupadd --system app && useradd --system --gid app --uid 10001 app
WORKDIR /app
COPY app.py settings.ini ./
# "keep the settings private": only the owner (root) may read them now
RUN chmod 600 settings.ini
USER app
EXPOSE 8080
CMD ["python", "app.py"]
