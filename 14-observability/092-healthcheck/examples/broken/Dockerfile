FROM nginx:1.30-alpine
# checks the web server every 2 s; 3 failures in a row = unhealthy
HEALTHCHECK --interval=2s --timeout=3s --start-period=2s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:8080/ || exit 1
