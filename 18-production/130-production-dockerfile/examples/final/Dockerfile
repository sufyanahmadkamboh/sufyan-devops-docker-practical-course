# Production Dockerfile for examples/node-api (lesson 130)
FROM node:24-alpine

# runtime settings that never change between environments
ENV NODE_ENV=production
WORKDIR /app

# dependencies first: this layer is rebuilt only when the lock file changes
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# then the application code, owned by root and read-only for the app user
COPY server.js ./

# never run as root (the node image has an unprivileged user "node")
USER node
EXPOSE 3000

# the engine checks that the app answers, not only that the process exists
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:3000/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]

LABEL org.opencontainers.image.title="node-api" \
      org.opencontainers.image.description="Small HTTP API of the Docker Practical Course" \
      org.opencontainers.image.licenses="MIT"

# exec form: node is PID 1 and receives SIGTERM directly
CMD ["node", "server.js"]
