# stage 1, "build": the Go toolchain compiles the program
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 go build -o /out/go-api .

# stage 2, the image we ship: a plain Alpine with only the binary
FROM alpine:3.23
COPY --from=build /out/go-api /usr/local/bin/go-api
USER nobody
EXPOSE 8080
CMD ["go-api"]
