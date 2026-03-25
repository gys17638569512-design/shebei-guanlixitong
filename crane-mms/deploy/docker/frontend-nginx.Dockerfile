FROM node:20-bookworm-slim AS admin-builder

WORKDIR /build/frontend-pc
COPY frontend-pc/package.json frontend-pc/package-lock.json ./
RUN npm config set registry https://registry.npmmirror.com
RUN npm ci
COPY frontend-pc/ ./
RUN npm run build

FROM node:20-bookworm-slim AS portal-builder

WORKDIR /build/frontend-portal
COPY frontend-portal/package.json frontend-portal/package-lock.json ./
RUN npm config set registry https://registry.npmmirror.com
RUN npm ci
COPY frontend-portal/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY deploy/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=admin-builder /build/frontend-pc/dist /usr/share/nginx/html/admin
COPY --from=portal-builder /build/frontend-portal/dist /usr/share/nginx/html/portal

EXPOSE 80
EXPOSE 8080
