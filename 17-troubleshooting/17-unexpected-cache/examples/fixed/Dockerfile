FROM alpine:3.23
# A changing build argument changes the cache key of every step after it: pass a new value whenever the
# downloaded content must be fresh (CI passes the date or the pipeline run number).
ARG RATES_VERSION=unset
RUN echo "exchange rates fetched at $(date -u +%H:%M:%S) (rates version $RATES_VERSION)" > /rates.txt
COPY show-rates.sh /show-rates.sh
CMD ["sh", "/show-rates.sh"]
