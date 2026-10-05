# "daemon off;" keeps nginx in the foreground: it stays process 1 and the container keeps running
FROM nginx:1.30-alpine
COPY index.html /usr/share/nginx/html/index.html
CMD ["nginx", "-g", "daemon off;"]
