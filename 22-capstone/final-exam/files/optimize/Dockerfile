# Works, but the image carries the whole Go toolchain and the source code. Task 9: make it small.
FROM golang:1.26-alpine
WORKDIR /src
COPY . .
RUN go build -o /usr/local/bin/go-api .
EXPOSE 8080
CMD ["go-api"]
