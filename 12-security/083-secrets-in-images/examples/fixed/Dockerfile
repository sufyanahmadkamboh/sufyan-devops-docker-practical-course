FROM alpine:3.23
# the secret is mounted only while this RUN step runs: it is never written to a layer, the history or the metadata
RUN --mount=type=secret,id=api_token \
    test -s /run/secrets/api_token && echo "token available during this step only" > /dev/null
# runtime secrets (database passwords) are given when the container starts, never in the image (lesson 061)
CMD ["sh", "-c", "echo app started"]
