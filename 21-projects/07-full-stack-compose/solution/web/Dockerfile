FROM nginx:1.30-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/site.conf
COPY index.html app.js /usr/share/nginx/html/
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/healthz"]
