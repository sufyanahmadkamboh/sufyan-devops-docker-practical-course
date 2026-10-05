# syntax=docker/dockerfile:1
# Stage 1: compile a static binary (no C library needed: CGO_ENABLED=0).
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY *.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

# Stage 2: only the binary, on distroless static: no shell, no package manager, user 65532.
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/go-api /go-api
EXPOSE 8080
ENTRYPOINT ["/go-api"]
