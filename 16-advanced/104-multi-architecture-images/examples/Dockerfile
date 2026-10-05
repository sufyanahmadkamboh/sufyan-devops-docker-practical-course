# The build stage always runs on the build machine's own platform ($BUILDPLATFORM), so no emulation is needed:
# Go cross-compiles for the target platform that buildx asks for ($TARGETOS/$TARGETARCH).
FROM --platform=$BUILDPLATFORM golang:1.26-alpine AS build
ARG TARGETOS TARGETARCH
WORKDIR /src
COPY go.mod main.go ./
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/hello .

# The final image contains only the static binary: no base image has to be downloaded for any platform.
FROM scratch
COPY --from=build /out/hello /hello
USER 65534:65534
ENTRYPOINT ["/hello"]
