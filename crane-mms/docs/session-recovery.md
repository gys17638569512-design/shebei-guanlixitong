## Session Recovery Record

Last updated: 2026-03-25 (Asia/Shanghai)

### Current focus

- Primary task: continue production deployment and verification for `crane-mms`.
- Current deployment target provided by user: Alibaba Cloud ECS Ubuntu server.
- Recovery goal: if chat history is lost again, use this file to quickly reconstruct task state and respawn needed subagents.

### Workspace state

- Repo path: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms`
- Branch: `main`
- HEAD commit at recovery record time: `ed382c6ac8623f09d412934d1b438c67c01a683d`

### Recent completed work

- Backend permission verification path was unblocked.
- Added test bootstrap env for backend tests.
- Fixed backend static/uploads mounting to use paths relative to backend source directory.
- Deferred PDF service imports in some routers so unrelated tests are not blocked by optional PDF dependencies during app import.
- Verified backend permission test file passes.
- Verified both frontend builds succeed outside sandbox.
- Fixed admin frontend production API base URL handling and added a regression verification script.
- Prepared Ubuntu Docker deployment bundle and uploaded it to `/srv/crane-mms/app`.
- Installed lightweight desktop stack on server: `xfce4`, `xrdp`, `xorgxrdp`, `dbus-x11`.
- Added `2G` swap on server at `/swapfile`.
- Installed Docker runtime on server and configured China registry mirrors.
- Fixed backend Docker build failures caused by missing `pycairo` system dependencies.
- Switched backend image Python package installation to a Tsinghua PyPI mirror and removed unnecessary `pip` self-upgrade during image build.
- Fixed backend runtime crash caused by missing `python-dateutil` in `backend/requirements.txt`.
- Completed Docker deployment successfully: `mysql`, `backend`, and `nginx` containers are running and healthy where applicable.
- Enabled SSH key login from this workstation to the server for future recovery and unattended ops.
- Fixed production report archive API crash in `backend/routers/report.py` by replacing the nonexistent `WorkOrder.completed_at` reference with archive-time fallback based on `updated_at` / `created_at`.
- Added backend regression test `backend/tests/test_report_archive.py` to keep `/api/v1/orders/reports/archive` from regressing.
- Redeployed only the backend service and verified production report archive API now returns `200`.
- Re-ran management-side report center verification; `/system/reports` now loads normally in the empty-data scenario.

### Files changed in current local work

- `backend/tests/conftest.py`
- `backend/main.py`
- `backend/routers/order.py`
- `backend/routers/repair.py`
- `backend/routers/report.py`
- `backend/requirements.txt`
- `backend/tests/test_report_archive.py`
- `frontend-pc/src/utils/request.js`
- `frontend-pc/vite.config.js`
- `frontend-pc/scripts/verify-request-config.mjs`
- `deploy/docker/backend.Dockerfile`
- `deploy/docker/frontend-nginx.Dockerfile`

### Latest verification evidence

- Backend:
  - Command: `python -m pytest backend/tests/test_settings_permission_management.py -q`
  - Result: `3 passed`
- Backend regression:
  - Command: `python -m pytest tests/test_report_archive.py tests/test_smoke.py -q`
  - Result: `3 passed`
- Frontend admin:
  - Command: `npm run build`
  - Result: build succeeds outside sandbox
- Frontend portal:
  - Command: `npm run build`
  - Result: build succeeds outside sandbox
- Important note:
  - `spawn EPERM` seen in sandboxed frontend builds was identified as environment/sandbox behavior, not current repo build breakage.
- Deployment runtime:
  - Command: `docker compose -f /srv/crane-mms/app/deploy/docker/docker-compose.yml --env-file /srv/crane-mms/app/deploy/docker/.env.production ps`
  - Result: `crane-mms-mysql`, `crane-mms-backend`, `crane-mms-nginx` running; `mysql` healthy; `backend` healthy
- Server-local HTTP verification:
  - `curl -I http://127.0.0.1/` -> `200 OK`
  - `curl -I http://127.0.0.1:8080/` -> `200 OK`
  - `curl -I http://127.0.0.1/login` -> `200 OK`
  - `curl -I http://127.0.0.1:8080/login` -> `200 OK`
  - `curl -I http://127.0.0.1/static/brand-mark.svg` -> `200 OK`
- Important note:
  - External HTTP verification from the current Codex runtime was inconclusive: TCP connect to `47.95.157.135:80/8080` succeeded, but no HTTP response body/headers were returned to this environment, and those requests did not appear in server nginx access logs.
  - Because the server itself is listening on `0.0.0.0:80` and `0.0.0.0:8080`, host firewall is inactive, and local curl works, if the user still cannot access externally, check Alibaba Cloud ECS security group / public ingress rules for `80`, `8080`, `3389`, and `22`.
- Production report center repair:
  - Deploy action: synced `backend/routers/report.py`, rebuilt only `backend`, backend container healthy
  - API verification: `GET http://47.95.157.135/api/v1/orders/reports/archive` -> `200`, body summary `{"code":200,"msg":"success","data":[]}`
  - UI retest: `/system/reports` opens successfully; empty-state renders without console errors
  - Evidence:
    - `docs/testing/admin-functional-test-report-2026-03-25.md`
    - `output/playwright/admin-functional-test-2026-03-25-retest-reports/`

### Active handoff snapshot

- Deployment subagent id: `019d1e2f-b7c1-70b3-856d-b8bdf2ec3819`
- Testing subagent id: `019d22ce-99bf-70e1-a27b-93a6297f1353` (`Turing`)
- Status when this record was written:
  - deployment subagent completed backend-only production redeploy for report center fix
  - testing subagent completed report center UI retest after deploy

### Server details already provided by user

- Provider: Alibaba Cloud ECS
- Region: `华北 2（北京）`
- Current active server:
  - Public IP: `47.95.157.135`
  - OS: `Ubuntu 24.04.4 LTS`
  - Approx machine size: `2 vCPU / 2 GiB RAM / 40 GiB disk`
  - SSH login verified with `root`
  - Hostname: `iZmo98m3b2m0z2Z`
  - SSH key login from this workstation is configured and verified
- Previous temporary server state before replacement:
  - Public IP: `47.95.15.7`
  - OS: `Windows Server 2025 数据中心版 64 位中文版`
  - Login style shown by screenshot: terminal connection, password auth, username `Administrator`

### Sensitive credential handling

- User provided login credential via screenshot in chat.
- For security, the plaintext password is intentionally **not** stored in this workspace file.
- If credentials are needed after chat loss, ask the user to resend them or reuse the locally saved Workbench credential if still present on the machine.

### What cannot be truly restored automatically

- Lost desktop UI chat history cannot be reattached to a new window by this repo alone.
- Old subagent runtime state may not survive app/session restart.

### How to recover quickly next time

1. Open this file first.
2. Reconstruct context from "Current focus", "Recent completed work", and "Latest verification evidence".
3. Reuse SSH key login to `root@47.95.157.135` first before asking user for credentials.
4. If needed, respawn a deployment subagent and assign it deployment monitoring / verification.
5. Reuse the non-sensitive server facts from this file.
6. Ask the user to resend any secret not stored here only if the saved workstation credential and SSH key both stop working.

### Current production status

- SSH to `47.95.157.135:22` verified with both password auth and key auth
- Lightweight GUI stack installed: `xfce4`, `xrdp`, `xorgxrdp`
- `xrdp` is enabled and listening on `3389`
- Swap added: `/swapfile` 2G
- Docker app deployed at `/srv/crane-mms/app`
- Public-facing services:
  - admin: `http://47.95.157.135/login`
  - portal: `http://47.95.157.135:8080/login`
- Backend admin account exists in production database and login is verified
- Report center fix is live:
  - `/api/v1/orders/reports/archive` returns `200`
  - `/system/reports` renders normally in the current empty-data state

### Next expected step

- Continue with the next user-requested feature, design, testing, or deployment task from the now-stable production baseline.
