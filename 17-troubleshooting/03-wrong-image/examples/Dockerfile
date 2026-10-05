# A tiny web server that answers with the version it was built as
FROM busybox:1.37
ARG VERSION=dev
RUN mkdir /www && echo "price-list version $VERSION" > /www/index.html
LABEL org.opencontainers.image.version=$VERSION
EXPOSE 8080
CMD ["httpd", "-f", "-p", "8080", "-h", "/www"]
