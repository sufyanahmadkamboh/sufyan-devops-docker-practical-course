# One stage: the image ships the whole Go toolchain and the source code to run one small binary
FROM golang:1.26-alpine
WORKDIR /src
COPY . .
RUN go build -o /usr/local/bin/api .
EXPOSE 8080
CMD ["api"]
