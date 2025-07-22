# 使用官方Python镜像替代GitHub Container Registry
FROM python:3.10-slim-bookworm

# 设置pip和apt使用国内镜像源
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
    PIP_TRUSTED_HOST=mirrors.aliyun.com

# 安装uv包管理器
RUN pip install uv

WORKDIR /app

RUN mkdir -p /app/data /app/logs

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 完全替换apt源为阿里云镜像，并清理默认配置
RUN rm -f /etc/apt/sources.list.d/* && \
    echo 'deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free' > /etc/apt/sources.list && \
    echo 'deb-src http://mirrors.aliyun.com/debian/ bookworm main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb-src http://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free' >> /etc/apt/sources.list && \
    echo 'deb-src http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free' >> /etc/apt/sources.list && \
    echo 'Acquire::http::Pipeline-Depth 0;' > /etc/apt/apt.conf.d/99disable-pipeline && \
    echo 'Acquire::http::No-Cache true;' >> /etc/apt/apt.conf.d/99disable-pipeline && \
    echo 'Acquire::BrokenProxy true;' >> /etc/apt/apt.conf.d/99disable-pipeline && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wkhtmltopdf \
    xvfb \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-liberation \
    pandoc \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 启动Xvfb虚拟显示器
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 -ac +extension GLX &\nexport DISPLAY=:99\nexec "$@"' > /usr/local/bin/start-xvfb.sh \
    && chmod +x /usr/local/bin/start-xvfb.sh

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制日志配置文件
COPY config/ ./config/

COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "web/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
