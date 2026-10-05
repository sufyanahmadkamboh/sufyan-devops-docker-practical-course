# One Dockerfile, three stages: the pipeline tests with --target test and ships --target production
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
EXPOSE 3000
CMD ["node", "server.js"]
