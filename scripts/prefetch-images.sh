#!/usr/bin/env bash
# prefetch-images.sh: download every image the course uses, once.
#
# Docker Hub limits anonymous pulls per IP address. If you hit "toomanyrequests: You have reached your
# unauthenticated pull rate limit", either log in to Docker Hub (docker login) or run this script with --mirror: it
# pulls the same official images through Google's public Docker Hub mirror (mirror.gcr.io) and tags them with their
# usual names, so every lesson finds them locally.
#
#   bash scripts/prefetch-images.sh            pull from Docker Hub
#   bash scripts/prefetch-images.sh --mirror   pull through mirror.gcr.io (no Docker Hub rate limit)
set -euo pipefail

IMAGES=(
  hello-world:latest
  alpine:3.23 busybox:1.37 ubuntu:24.04 debian:13-slim
  nginx:1.30-alpine nginx:1.29-alpine
  node:24-alpine python:3.14-slim python:3.14-alpine golang:1.26-alpine
  eclipse-temurin:25-jdk-alpine eclipse-temurin:25-jre-alpine php:8.5-fpm-alpine
  postgres:18-alpine redis:8-alpine registry:3
)
OTHER=(gcr.io/distroless/static-debian12:nonroot)

mirror=false
[ "${1:-}" = "--mirror" ] && mirror=true

for image in "${IMAGES[@]}"; do
  if docker image inspect "$image" > /dev/null 2>&1; then
    echo "cached   $image"
  elif $mirror; then
    docker pull -q "mirror.gcr.io/library/$image" > /dev/null
    docker tag "mirror.gcr.io/library/$image" "$image"
    docker rmi -f "mirror.gcr.io/library/$image" > /dev/null
    echo "mirror   $image"
  else
    docker pull -q "$image" > /dev/null
    echo "pulled   $image"
  fi
done
for image in "${OTHER[@]}"; do
  docker image inspect "$image" > /dev/null 2>&1 || docker pull -q "$image" > /dev/null
  echo "ready    $image"
done
