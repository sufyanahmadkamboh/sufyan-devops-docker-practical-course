FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY main.go ./
# static (CGO_ENABLED=0) and smaller: -trimpath removes local paths, -s -w drop debug symbols
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

# distroless: no shell, no package manager, CA certificates and a non-root user (uid 65532) included
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/go-api /go-api
EXPOSE 8080
# exec form is required: there is no /bin/sh to run a shell-form command
ENTRYPOINT ["/go-api"]
