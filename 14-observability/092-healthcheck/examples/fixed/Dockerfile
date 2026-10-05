FROM nginx:1.30-alpine
# checks the web server every 2 s; 3 failures in a row = unhealthy
# nginx listens on port 80 inside the container; wget is part of BusyBox in the Alpine-based image
HEALTHCHECK --interval=2s --timeout=3s --start-period=2s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:80/ || exit 1
