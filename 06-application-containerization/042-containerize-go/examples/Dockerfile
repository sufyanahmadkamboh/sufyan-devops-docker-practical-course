FROM golang:1.26-alpine
WORKDIR /src
# module files first: dependencies are downloaded once and cached (lesson 039)
COPY go.mod ./
RUN go mod download
COPY main.go ./
# CGO_ENABLED=0: a static binary that needs no C library (lesson 089 relies on it)
RUN CGO_ENABLED=0 go build -o /usr/local/bin/go-api .
USER nobody
EXPOSE 8080
CMD ["go-api"]
