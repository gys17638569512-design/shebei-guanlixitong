FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|http://deb.debian.org/debian|https://mirrors.aliyun.com/debian|g; s|http://deb.debian.org/debian-security|https://mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list.d/debian.sources; \
      fi \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        pkg-config \
        libcairo2-dev \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        shared-mime-info \
        fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/backend/

RUN mkdir -p /app/backend/uploads /app/backend/tmp

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
