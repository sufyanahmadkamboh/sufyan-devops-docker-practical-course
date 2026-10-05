# syntax=docker/dockerfile:1
# Stage 1: install the production dependencies exactly as locked (npm ci). npm and its cache stay in this stage.
FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# (mkdir: this API has no dependencies yet, and npm ci creates no node_modules folder then)
RUN npm ci --omit=dev && mkdir -p node_modules

# Stage 2: the runtime: Node.js, the dependencies and the code, as the unprivileged "node" user.
FROM node:24-alpine
ENV NODE_ENV=production PORT=3000
WORKDIR /app
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node package.json server.js ./
USER node
EXPOSE 3000
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:3000/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]
# exec form: node is process 1 and receives SIGTERM from docker stop directly
CMD ["node", "server.js"]
