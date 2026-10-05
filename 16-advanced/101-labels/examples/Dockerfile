FROM nginx:1.30-alpine
# standard OCI image labels: who made the image, from which source, which version
ARG VERSION=dev
ARG REVISION=unknown
LABEL org.opencontainers.image.title="cafe-web" \
      org.opencontainers.image.description="The cafe's static website" \
      org.opencontainers.image.source="https://github.com/example/cafe-web" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.licenses="MIT"
