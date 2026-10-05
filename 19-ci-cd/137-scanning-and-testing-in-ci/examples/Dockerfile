# The Dockerfile of lesson 135, with a HEALTHCHECK in the production stage (lesson 137)
FROM node:24-alpine AS base
ENV NODE_ENV=production
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server.js ./

# the tests (test/*.test.js) run inside the build: if one fails, the build fails and nothing is shipped
FROM base AS test
COPY test/ ./test/
RUN node --test

# the image that is shipped: no tests, no root
FROM base AS production
USER node
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:3000/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]
EXPOSE 3000
CMD ["node", "server.js"]
