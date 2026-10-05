# price: a command-line tool in an image
FROM alpine:3.23
COPY menu.csv /app/
COPY --chmod=0755 price.sh /usr/local/bin/price
ENTRYPOINT ["price"]
