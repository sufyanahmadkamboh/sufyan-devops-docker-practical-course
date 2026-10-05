FROM alpine:3.23
# Fetch the latest exchange rates at build time. The current time stands in for the downloaded content: in a real
# project this is "curl https://…/rates.json", "git clone …" or "apk upgrade".
RUN echo "exchange rates fetched at $(date -u +%H:%M:%S)" > /rates.txt
COPY show-rates.sh /show-rates.sh
CMD ["sh", "/show-rates.sh"]
