FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置国内 apt 源
RUN echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY . .

# 安装 uv 包管理器
RUN pip install --no-cache-dir uv

# 使用 uv 安装依赖
RUN uv sync --no-dev

# 暴露端口
EXPOSE 8000

# 设置启动命令
CMD ["python", "Bot.py"]