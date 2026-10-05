# Download, use and delete a 20 MB file in separate steps
FROM alpine:3.23
RUN dd if=/dev/zero of=/tmp/big.bin bs=1M count=20
RUN rm /tmp/big.bin
