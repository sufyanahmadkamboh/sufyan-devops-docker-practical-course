# stage "build": compile the Go API
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod main.go ./
RUN CGO_ENABLED=0 go build -o /out/go-api .

# stage "export": only the compiled binary; used with --output to get files instead of an image
FROM scratch AS export
COPY --from=build /out/go-api /

# stage "image" (the default, last stage): the runnable image
FROM gcr.io/distroless/static-debian12:nonroot AS image
COPY --from=build /out/go-api /go-api
EXPOSE 8080
ENTRYPOINT ["/go-api"]
