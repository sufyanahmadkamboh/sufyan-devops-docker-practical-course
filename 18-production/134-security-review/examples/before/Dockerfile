# The image under review (lesson 134): it works, and it has nine findings
FROM node:24-alpine
ENV DB_PASSWORD=example-password-change-me
ARG NPM_TOKEN=example-npm-token-change-me
RUN apk add --no-cache curl bash
COPY . .
RUN npm install
EXPOSE 3000
CMD npm start
