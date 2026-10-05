# syntax=docker/dockerfile:1
# Build stage: Node.js builds the static files. Node.js itself never reaches the final image.
FROM node:24-alpine AS build
WORKDIR /app
COPY build.mjs ./
COPY src/ src/
ARG APP_VERSION=dev
RUN APP_VERSION=${APP_VERSION} node build.mjs

# Final stage: Nginx serves the files as the unprivileged nginx user (101) on port 8080.
FROM nginx:1.30-alpine
ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="capstone-frontend" \
      org.opencontainers.image.version="${APP_VERSION}"
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist/ /usr/share/nginx/html/
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/healthz"]
