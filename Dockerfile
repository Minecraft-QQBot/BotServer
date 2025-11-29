FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml ./
COPY . .

# 安装 uv 包管理器
RUN pip install --no-cache-dir uv -i https://mirrors.aliyun.com/pypi/simple

# 使用 uv 安装依赖
RUN uv sync
RUN uv cache clean

# 暴露端口
EXPOSE 8000

# 设置启动命令
CMD ["/app/.venv/bin/python", "Bot.py"]