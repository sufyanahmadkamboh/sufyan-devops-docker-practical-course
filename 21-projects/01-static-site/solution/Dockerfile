# A static site on Nginx: custom configuration, non-root, with a healthcheck.
FROM nginx:1.30-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html styles.css /usr/share/nginx/html/
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/healthz"]
