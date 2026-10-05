# nginx starts as a background daemon by default: the main process exits and the container stops with it
FROM nginx:1.30-alpine
COPY index.html /usr/share/nginx/html/index.html
CMD ["nginx"]
