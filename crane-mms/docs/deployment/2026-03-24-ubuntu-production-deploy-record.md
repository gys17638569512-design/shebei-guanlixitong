# Ubuntu Production Deploy Record

## Purpose

这份文档用于记录 Ubuntu 24.04 生产环境的实际部署信息，确保聊天记录丢失后仍可从文档继续执行、验证、回滚。

## Environment Baseline

- System: Ubuntu 24.04 LTS 64-bit
- Network: Internal network only
- Runtime: Docker Compose
- Database: MySQL container
- Reverse proxy: Nginx container

## Server Inventory

- Hostname:
- Internal IP:
- SSH user:
- Deploy operator:
- Deploy date:

## Directory Layout

- Repo path:
- Runtime root:
- `runtime/mysql`
- `runtime/uploads`
- `runtime/logs/backend`
- `runtime/logs/nginx`

## Required Software Versions

- Docker:
- Docker Compose:

## Images and Containers

- Backend image tag:
- Frontend/Nginx image tag:
- MySQL image tag:
- Running containers:

## Secrets Checklist

Only record whether each secret has been filled. Do not record plaintext values.

- `MYSQL_ROOT_PASSWORD`: filled / pending
- `MYSQL_PASSWORD`: filled / pending
- `SECRET_KEY`: filled / pending
- `CUSTOMER_JWT_SECRET`: filled / pending
- COS credentials: filled / pending / skipped
- e签宝 credentials: filled / pending / skipped
- SMS credentials: filled / pending / skipped
- 微信 credentials: filled / pending / skipped

## Deployment Steps

### 1. Prepare files

- Copy `deploy/docker/.env.production.example` to `.env.production`
- Fill required secrets
- Ensure runtime directories exist

### 2. Build and start

```bash
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production build
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production up -d
```

### 3. Inspect status

```bash
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production ps
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production logs backend --tail=200
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production logs nginx --tail=200
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production logs mysql --tail=200
```

## Validation Checklist

- [ ] `docker compose config` succeeds
- [ ] MySQL container is healthy
- [ ] Backend container is healthy
- [ ] Nginx container is running
- [ ] `GET /health` returns 200
- [ ] Admin frontend is reachable
- [ ] Portal frontend is reachable
- [ ] Login works
- [ ] Static file access works
- [ ] Upload/report path works

## Rollback Procedure

### Rollback to previous image

```bash
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production down
docker image ls
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production up -d
```

### Emergency stop

```bash
docker compose -f deploy/docker/docker-compose.yml --env-file deploy/docker/.env.production down
```

### Data protection notes

- Do not delete `runtime/mysql`
- Do not delete `runtime/uploads`
- Back up `.env.production` securely before major changes

## Change Log

- 2026-03-24: Initial deployment template created
