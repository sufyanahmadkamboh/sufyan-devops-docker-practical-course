FROM alpine:3.23
# The private price feed needs a token during the build. (The test stands in for
# "wget --header "Authorization: Bearer $API_TOKEN" https://feed.example.com/prices".)
ARG API_TOKEN
RUN test -n "$API_TOKEN" && echo "price feed downloaded" > /feed.txt
CMD ["cat", "/feed.txt"]
