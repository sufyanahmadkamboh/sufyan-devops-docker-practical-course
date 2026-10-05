# go-api: built in a Go image, shipped in a minimal non-root image (lesson 089)
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY *.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/go-api /go-api
EXPOSE 8080
ENTRYPOINT ["/go-api"]
