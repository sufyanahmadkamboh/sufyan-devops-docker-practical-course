# The configuration is part of the image (immutable): a configuration change is a new, versioned image.
FROM nginx:1.30-alpine
COPY nginx.conf /etc/nginx/nginx.conf
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/healthz"]
