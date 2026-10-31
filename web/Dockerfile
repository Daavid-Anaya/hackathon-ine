# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim@sha256:4b150b48b4116e2a22f2c39cc27025fbf4f153e2078fd3b14d159fdb5c7279da AS build

ENV CI=true
WORKDIR /app
RUN chown node:node /app
USER node
COPY --chown=node:node package.json package-lock.json ./
RUN npm ci --include=dev --no-audit --no-fund
COPY --chown=node:node index.html vite.config.ts tsconfig.json ./
COPY --chown=node:node src/ ./src/
RUN npm run build

# Las pruebas de navegador son opcionales y no se incluyen en la imagen que sirve la web.
FROM build AS checks
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium \
    && rm -rf /var/lib/apt/lists/*
COPY --chown=node:node tests/ ./tests/
ENV WEB_BROWSER_PATH=/usr/bin/chromium \
    HOME=/tmp \
    NPM_CONFIG_CACHE=/tmp/.npm
USER node
CMD ["npm", "test"]

FROM nginxinc/nginx-unprivileged:stable-alpine@sha256:f5116ed4606f3eb015dd4a8e28cb9b351476dc0ad4bc6e9f93b19cec130cdf03 AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/ /usr/share/nginx/html/
USER 101:101
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:8080/ || exit 1
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
