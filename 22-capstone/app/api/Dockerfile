# syntax=docker/dockerfile:1
# Build stage: the Go toolchain, the source and the module cache. None of it reaches the final image.
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY *.go ./
ARG APP_VERSION=dev
RUN --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/api .

# Final stage: a static binary on distroless: no shell, no package manager, runs as user 65532 (nonroot).
FROM gcr.io/distroless/static-debian12:nonroot
ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="capstone-api" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.source="https://github.com/sufyanahmadkamboh/sufyan-devops-docker-practical-course"
ENV APP_VERSION=${APP_VERSION} PORT=8080
COPY --from=build /out/api /api
USER nonroot:nonroot
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 CMD ["/api", "-healthcheck"]
ENTRYPOINT ["/api"]
