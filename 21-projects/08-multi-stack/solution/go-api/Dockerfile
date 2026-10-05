FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod *.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

# alpine instead of distroless here: the healthcheck needs wget (project 04 shows the distroless variant)
FROM alpine:3.23
COPY --from=build /out/go-api /usr/local/bin/go-api
USER 65532:65532
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/health"]
ENTRYPOINT ["go-api"]
