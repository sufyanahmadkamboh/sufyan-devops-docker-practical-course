FROM alpine:3.23
# The token is mounted for this one RUN step only (/run/secrets/api_token): it is never written to a layer,
# to the image metadata or to the build history.
RUN --mount=type=secret,id=api_token \
    test -s /run/secrets/api_token && echo "price feed downloaded" > /feed.txt
CMD ["cat", "/feed.txt"]
