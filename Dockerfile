# Mem0Evomem Docker Image
# 基於 Python 3.10 的中文優化 AI 記憶系統

# 使用官方 Python 3.10 slim 鏡像（減少體積）
FROM python:3.10-slim

# 維護者信息
LABEL maintainer="EvoMem Team"
LABEL version="1.0.0"
LABEL description="Mem0Evomem - Chinese-optimized AI Memory System with BGE-M3"

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴（BGE-M3 需要的底層庫）
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenMP 支持（PyTorch 多線程）
    libgomp1 \
    # 清理 apt 緩存以減少鏡像大小
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
# --no-cache-dir: 不緩存下載的包，減少鏡像大小
# --upgrade: 確保使用最新兼容版本
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建非 root 用戶以提高安全性
RUN useradd -m -u 1000 appuser && \
    # 將應用目錄所有權轉移給 appuser
    chown -R appuser:appuser /app && \
    # 創建數據目錄
    mkdir -p /app/data /app/chroma_db && \
    chown -R appuser:appuser /app/data /app/chroma_db

# 切換到非 root 用戶
USER appuser

# 暴露端口（如果有 API 服務）
EXPOSE 8000

# 健康檢查（每 30 秒檢查一次）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# 設置環境變量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# 默認命令（可被 docker-compose 覆蓋）
CMD ["python", "-m", "pytest", "tests/integration/simple_e2e_test.py", "-v"]
