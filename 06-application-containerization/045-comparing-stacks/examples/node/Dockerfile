FROM node:24-alpine
ENV NODE_ENV=production
WORKDIR /app
# dependency manifests first (lesson 039), then a reproducible install from the lockfile
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY server.js ./
# the official image ships an unprivileged "node" user (lesson 081)
USER node
EXPOSE 3000
# exec form: node is PID 1 and receives SIGTERM from docker stop
CMD ["node", "server.js"]
