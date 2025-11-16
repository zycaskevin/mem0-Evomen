# Mem0Evomem 生產部署指南

**版本**: 1.0.0
**日期**: 2025-11-16
**狀態**: Week 3-4 生產部署準備

---

## 🎯 部署概覽

本指南涵蓋 Mem0Evomem + BGE-M3 的完整生產部署流程，包括：

- ✅ CI/CD 自動化流程
- ✅ 環境變量安全管理
- ✅ 數據備份與恢復
- ✅ 系統監控與告警
- ✅ 高可用性配置

---

## 📊 部署架構

```
GitHub Repository
    ↓
GitHub Actions (CI/CD)
    ├─ 自動測試 (pytest)
    ├─ Docker 構建
    ├─ 安全掃描 (Trivy)
    └─ 部署到環境
        ↓
GitHub Container Registry (ghcr.io)
    ↓
生產環境
    ├─ Staging (自動部署)
    └─ Production (手動批准)
```

---

## 🚀 快速部署

### 前置需求

1. **GitHub Repository 設置**
   - Fork 或 Clone 此專案
   - 設置 Repository Secrets

2. **必需的 Secrets**

```bash
# GitHub Repository Settings → Secrets and Variables → Actions

OPENAI_API_KEY=sk-...          # OpenAI API 密鑰
DOCKERHUB_USERNAME=your-user    # (可選) Docker Hub 帳號
DOCKERHUB_TOKEN=your-token      # (可選) Docker Hub Token
```

3. **環境配置**

```bash
# 複製環境變量範例
cp .env.example .env

# 編輯 .env 填入實際值
nano .env
```

---

## 📋 部署流程

### Step 1: 配置 CI/CD

**GitHub Actions Workflow** 已配置在 `.github/workflows/docker-build-push.yml`

**觸發條件**:
- Push to `main` 分支 → 自動測試 + 構建 + 部署到 Staging
- Pull Request → 僅測試
- Release 發布 → 部署到 Production

**Workflow 步驟**:

1. **測試階段**
   ```yaml
   - 安裝依賴
   - 運行 pytest 單元測試
   - 生成覆蓋率報告
   - 上傳到 Codecov
   ```

2. **構建階段**
   ```yaml
   - 構建 Docker 鏡像
   - 推送到 GitHub Container Registry
   - 運行 Trivy 安全掃描
   - 上傳安全報告
   ```

3. **部署階段**
   ```yaml
   - Staging: 自動部署 (main 分支)
   - Production: 手動批准 (Release)
   ```

---

### Step 2: 部署選項

#### Option 1: GitHub Container Registry + 手動部署

**1.1 拉取鏡像**

```bash
# 從 GitHub Container Registry 拉取
docker pull ghcr.io/zycaskevin/mem0-evomen:main

# 運行容器
docker run -d \
  --name mem0evomem \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  ghcr.io/zycaskevin/mem0-evomen:main
```

**1.2 使用 docker-compose**

```bash
# 修改 docker-compose.yml 使用 ghcr.io 鏡像
# image: ghcr.io/zycaskevin/mem0-evomen:main

docker-compose up -d
```

---

#### Option 2: AWS ECS/Fargate (推薦商用)

**2.1 創建 ECS 任務定義**

```bash
# 安裝 AWS CLI
pip install awscli

# 配置 AWS 憑證
aws configure

# 創建 ECS 集群
aws ecs create-cluster --cluster-name mem0evomem-cluster

# 註冊任務定義 (使用 deployment/aws-ecs-task-definition.json)
aws ecs register-task-definition \
  --cli-input-json file://deployment/aws-ecs-task-definition.json
```

**2.2 創建服務**

```bash
# 創建 ECS 服務
aws ecs create-service \
  --cluster mem0evomem-cluster \
  --service-name mem0evomem-service \
  --task-definition mem0evomem:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration \
    "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**成本估算**:
- Fargate (0.5 vCPU + 2GB RAM): ~$0.04/小時 = $29/月
- ECS 數據傳輸: ~$9/月
- **總計**: ~$38/月

---

#### Option 3: Google Cloud Run (最簡單)

**3.1 部署到 Cloud Run**

```bash
# 安裝 gcloud CLI
curl https://sdk.cloud.google.com | bash

# 初始化
gcloud init

# 構建並推送到 GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/mem0evomem

# 部署到 Cloud Run
gcloud run deploy mem0evomem \
  --image gcr.io/YOUR_PROJECT/mem0evomem \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --set-env-vars="$(cat .env | xargs)"
```

**優勢**:
- ✅ 自動擴展 (0 → N 實例)
- ✅ 按使用量計費
- ✅ 內建 HTTPS
- ✅ 簡單易用

**成本估算**:
- 前 180 萬請求/月免費
- 超出後: $0.00002/請求
- **預估**: $10-50/月 (中等流量)

---

#### Option 4: Azure Container Instances

**4.1 部署到 ACI**

```bash
# 安裝 Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 登入
az login

# 創建資源組
az group create --name mem0evomem-rg --location eastus

# 部署容器
az container create \
  --resource-group mem0evomem-rg \
  --name mem0evomem \
  --image ghcr.io/zycaskevin/mem0-evomen:main \
  --cpu 1 \
  --memory 2 \
  --environment-variables $(cat .env | xargs) \
  --ports 8000
```

---

### Step 3: 環境變量配置

**必填變量** (`.env`):

```bash
# 核心配置
ENVIRONMENT=production
OPENAI_API_KEY=sk-...

# BGE-M3 配置
BGE_M3_DEVICE=cpu
BGE_M3_USE_FP16=true

# ChromaDB
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db

# 監控
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

**安全最佳實踐**:

1. **使用 Secret 管理服務**
   - AWS: AWS Secrets Manager
   - GCP: Secret Manager
   - Azure: Key Vault

2. **不要在 Git 中存儲 Secrets**
   ```bash
   # .gitignore 已包含
   .env
   .env.local
   .env.production
   ```

3. **使用環境變量注入**
   ```bash
   # 在 CI/CD 中設置
   - name: Set environment variables
     env:
       OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
   ```

---

### Step 4: 數據備份策略

**4.1 自動備份腳本**

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="./data/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 備份 ChromaDB
tar -czf "$BACKUP_DIR/chroma_$DATE.tar.gz" ./data/chroma_db

# 備份環境配置
cp .env "$BACKUP_DIR/env_$DATE.backup"

# 清理舊備份 (保留 30 天)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: chroma_$DATE.tar.gz"
```

**4.2 自動化備份 (Cron)**

```bash
# 每天凌晨 2 點備份
0 2 * * * /app/scripts/backup.sh >> /app/logs/backup.log 2>&1
```

**4.3 恢復流程**

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1

# 停止服務
docker-compose down

# 恢復數據
tar -xzf "$BACKUP_FILE" -C ./data/

# 重啟服務
docker-compose up -d

echo "✅ Restore completed from $BACKUP_FILE"
```

---

### Step 5: 監控與告警

**5.1 健康檢查**

```bash
# Docker Compose 健康檢查已配置
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**5.2 Prometheus 指標 (可選)**

```python
# 在應用中集成 Prometheus
from prometheus_client import Counter, Histogram, start_http_server

# 定義指標
embedding_requests = Counter('embedding_requests_total', 'Total embedding requests')
embedding_latency = Histogram('embedding_latency_seconds', 'Embedding latency')

# 啟動指標服務
start_http_server(9090)
```

**5.3 告警配置 (示例)**

```yaml
# Alertmanager 配置
alerts:
  - name: HighMemoryUsage
    condition: memory_usage > 80%
    action: send_email

  - name: HighLatency
    condition: p95_latency > 1000ms
    action: send_slack_message
```

---

## 🔍 故障排除

### 常見問題

**1. 容器啟動失敗**

```bash
# 檢查日誌
docker logs mem0evomem

# 常見原因:
# - OPENAI_API_KEY 未設置
# - 記憶體不足 (需要 >=2GB)
# - 端口衝突
```

**2. BGE-M3 模型下載失敗**

```bash
# 手動預下載模型
python -c "from FlagEmbedding import BGEM3FlagModel; BGEM3FlagModel('BAAI/bge-m3')"

# 或使用鏡像站
export HF_ENDPOINT=https://hf-mirror.com
```

**3. ChromaDB 數據丟失**

```bash
# 確保數據卷正確掛載
docker inspect mem0evomem | grep Mounts

# 應該看到:
# "Source": "/path/to/data",
# "Destination": "/app/data"
```

---

## 📊 性能優化

### 生產環境建議配置

| 配置項 | 開發環境 | 生產環境 |
|--------|---------|---------|
| CPU | 1 核 | 2-4 核 |
| RAM | 2 GB | 4-8 GB |
| BGE-M3 Device | CPU | GPU (如可用) |
| BGE-M3 FP16 | True | True |
| 日誌級別 | DEBUG | INFO |
| 備份頻率 | 手動 | 每日自動 |
| 監控 | 可選 | 必需 |

---

## 🎯 下一步

完成生產部署後:

1. **監控系統運行** (1-2 週)
2. **調整資源配置** (根據實際負載)
3. **設置告警閾值** (基於歷史數據)
4. **制定擴展計劃** (如流量增長)

---

## 📞 支持與聯繫

**問題回報**: [GitHub Issues](https://github.com/zycaskevin/mem0-Evomen/issues)
**技術文檔**: [CLAUDE.md](CLAUDE.md)
**Docker 快速指南**: [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

---

**生產部署檢查清單** ✅

- [ ] GitHub Actions 配置完成
- [ ] 環境變量正確設置
- [ ] 數據備份腳本測試通過
- [ ] 健康檢查正常運行
- [ ] 監控系統已部署
- [ ] 告警機制已配置
- [ ] 災難恢復流程已測試
- [ ] 團隊成員已培訓

---

**維護者**: EvoMem Team
**最後更新**: 2025-11-16
**版本**: 1.0.0
