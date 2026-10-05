FROM alpine:3.23
# three common ways to leak a secret into an image (all of them are visible to anyone who has the image)
ARG API_TOKEN
ENV DB_PASSWORD=example-password-change-me
RUN echo "downloading private packages with token ${API_TOKEN}" > /dev/null
COPY credentials.txt /tmp/credentials.txt
RUN cat /tmp/credentials.txt > /dev/null && rm /tmp/credentials.txt
CMD ["sh", "-c", "echo app started"]
