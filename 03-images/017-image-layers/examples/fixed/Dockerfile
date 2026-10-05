# Create, use and delete the file in the same step: it never reaches a layer
FROM alpine:3.23
RUN dd if=/dev/zero of=/tmp/big.bin bs=1M count=20 \
 && rm /tmp/big.bin
