# Mem0Evomem 監控系統文檔

**版本**: v1.0
**創建日期**: 2025-11-16
**維護者**: EvoMem Team

---

## 🎯 系統架構

```
Mem0Evomem Application
        ↓
    Prometheus (指標收集)
        ↓
    Grafana (可視化)
        ↓
  AlertManager (告警)
```

### 核心組件

| 組件 | 版本 | 端口 | 功能 |
|------|------|------|------|
| Prometheus | 2.48.0 | 9090 | 指標收集與存儲 |
| Grafana | 10.2.2 | 3000 | 數據可視化 |
| Node Exporter | 1.7.0 | 9100 | 系統指標 |
| cAdvisor | 0.47.0 | 8080 | 容器指標 |
| AlertManager | 0.26.0 | 9093 | 告警管理 |

---

## 🚀 快速啟動

### 1. 啟動監控堆棧

```bash
# 啟動所有監控服務
docker-compose -f docker-compose.monitoring.yml up -d

# 查看服務狀態
docker-compose -f docker-compose.monitoring.yml ps

# 查看日誌
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 2. 訪問服務

| 服務 | URL | 默認憑證 |
|------|-----|---------|
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |
| AlertManager | http://localhost:9093 | - |
| cAdvisor | http://localhost:8080 | - |

### 3. 配置 Grafana

**首次登錄後**:
1. 修改默認密碼
2. 數據源已自動配置 (Prometheus)
3. 導入預設儀表板 (見下方)

---

## 📊 監控指標

### 系統層級指標 (Node Exporter)

- **CPU**: 使用率、負載、上下文切換
- **記憶體**: 總量、可用、使用率、Swap
- **磁碟**: I/O、空間使用率、IOPS
- **網絡**: 流量、錯誤率、連接數

### 容器層級指標 (cAdvisor)

- **資源使用**: CPU、記憶體、網絡、磁碟
- **容器狀態**: 運行、重啟、健康檢查
- **性能指標**: 延遲、吞吐量

### 應用層級指標 (自定義)

- **BGE-M3 Embedder**:
  - 嵌入延遲 (P50/P95/P99)
  - 吞吐量 (req/s)
  - 錯誤率
  - 批次大小分佈

- **ChromaDB**:
  - 查詢延遲
  - 插入速度
  - 索引大小
  - 連接池狀態

- **API**:
  - 請求速率
  - 錯誤率 (4xx/5xx)
  - 響應時間
  - 端點分佈

---

## 🚨 告警規則

### 系統告警 (`alerts/system_alerts.yml`)

| 告警 | 觸發條件 | 嚴重性 |
|------|---------|--------|
| HighCPUUsage | CPU > 80% (5分鐘) | Warning |
| CriticalCPUUsage | CPU > 95% (2分鐘) | Critical |
| HighMemoryUsage | Memory > 85% (5分鐘) | Warning |
| CriticalMemoryUsage | Memory > 95% (2分鐘) | Critical |
| LowDiskSpace | Disk < 20% (5分鐘) | Warning |
| CriticalDiskSpace | Disk < 10% (2分鐘) | Critical |

### 應用告警 (`alerts/application_alerts.yml`)

| 告警 | 觸發條件 | 嚴重性 |
|------|---------|--------|
| HighEmbeddingLatency | P95 > 500ms (5分鐘) | Warning |
| LowEmbeddingThroughput | < 1 req/s (5分鐘) | Warning |
| HighAPIErrorRate | 5xx > 5% (5分鐘) | Warning |
| CriticalAPIErrorRate | 5xx > 10% (2分鐘) | Critical |
| ContainerDown | 服務不可用 (1分鐘) | Critical |

---

## 📈 Grafana 儀表板

### 預設儀表板列表

1. **系統概覽** (`dashboards/system_overview.json`)
   - CPU、記憶體、磁碟、網絡
   - 系統負載與資源趨勢

2. **容器監控** (`dashboards/container_metrics.json`)
   - 容器資源使用
   - 重啟歷史
   - 健康狀態

3. **BGE-M3 性能** (`dashboards/bge_m3_performance.json`)
   - 嵌入延遲分佈
   - 吞吐量趨勢
   - 批次大小統計

4. **API 性能** (`dashboards/api_performance.json`)
   - 請求速率
   - 錯誤率
   - 響應時間分佈

### 導入儀表板

**方法 1: 自動導入** (已配置)
- 儀表板自動從 `monitoring/grafana/dashboards/` 載入

**方法 2: 手動導入**
1. 登錄 Grafana
2. Dashboard → Import
3. 上傳 JSON 文件或輸入儀表板 ID

---

## 🔧 配置文件說明

### `prometheus.yml`

**核心配置**:
```yaml
scrape_interval: 15s        # 抓取間隔
evaluation_interval: 15s   # 規則評估間隔
retention_time: 30d        # 數據保留 30 天
```

**抓取目標**:
- `mem0evomem`: 應用程序 (port 8000)
- `node-exporter`: 系統指標 (port 9100)
- `cadvisor`: 容器指標 (port 8080)
- `bge-m3`: Embedder 指標 (port 9090)

### `alertmanager.yml`

**告警路由**:
- Critical → Email + Slack
- Warning → Slack
- 告警抑制規則 (避免重複)

---

## 🎯 使用場景

### Scenario 1: 性能基準測試

```bash
# 1. 啟動監控
docker-compose -f docker-compose.monitoring.yml up -d

# 2. 執行性能測試
python scripts/benchmark_performance.py

# 3. 查看 Grafana 儀表板
# http://localhost:3000 → BGE-M3 Performance

# 4. 分析指標
# - P95 延遲趨勢
# - 吞吐量變化
# - 記憶體使用峰值
```

### Scenario 2: 生產環境監控

```bash
# 1. 配置告警接收器 (Email/Slack)
vim monitoring/alertmanager.yml

# 2. 啟動監控堆棧
docker-compose -f docker-compose.monitoring.yml up -d

# 3. 驗證告警規則
http://localhost:9090/alerts

# 4. 設置 Grafana 儀表板
# - 添加自定義面板
# - 設置告警閾值
# - 配置通知渠道
```

### Scenario 3: 故障排查

```bash
# 1. 檢查 Grafana 告警
http://localhost:3000/alerting/list

# 2. 查看 Prometheus 指標
http://localhost:9090/graph

# 3. 分析容器日誌
docker-compose -f docker-compose.monitoring.yml logs mem0evomem

# 4. 檢查資源使用
http://localhost:8080  # cAdvisor
```

---

## 📝 維護指南

### 日常維護

```bash
# 查看服務狀態
docker-compose -f docker-compose.monitoring.yml ps

# 重啟服務
docker-compose -f docker-compose.monitoring.yml restart

# 清理舊數據 (Prometheus 會自動清理 30 天前的數據)
docker volume inspect mem0evomem_prometheus_data
```

### 備份與恢復

```bash
# 備份 Prometheus 數據
docker run --rm -v mem0evomem_prometheus_data:/data \
  -v $(pwd)/backups:/backup ubuntu \
  tar czf /backup/prometheus_$(date +%Y%m%d).tar.gz /data

# 備份 Grafana 配置
docker run --rm -v mem0evomem_grafana_data:/data \
  -v $(pwd)/backups:/backup ubuntu \
  tar czf /backup/grafana_$(date +%Y%m%d).tar.gz /data
```

### 性能優化

**Prometheus 優化**:
- 調整 `retention_time` (默認 30天)
- 調整 `scrape_interval` (默認 15s)
- 啟用 TSDB 壓縮

**Grafana 優化**:
- 設置查詢緩存
- 限制面板數量
- 使用變量過濾

---

## 🔒 安全建議

1. **修改默認密碼**
   ```bash
   # Grafana
   GF_SECURITY_ADMIN_PASSWORD=your_secure_password
   ```

2. **啟用 HTTPS**
   - 使用 Nginx 反向代理
   - 配置 SSL 證書

3. **限制訪問**
   - 使用防火牆規則
   - 配置 OAuth 2.0

4. **定期更新**
   ```bash
   # 更新鏡像
   docker-compose -f docker-compose.monitoring.yml pull
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

---

## 📊 預期效果

### 監控覆蓋率

| 層級 | 監控項目 | 覆蓋率 |
|------|---------|--------|
| 系統層 | CPU/Memory/Disk/Network | 100% |
| 容器層 | Docker containers | 100% |
| 應用層 | BGE-M3/API/ChromaDB | 95% |

### 告警響應時間

- **Critical**: < 1 分鐘
- **Warning**: < 5 分鐘
- **Info**: < 15 分鐘

### 數據保留策略

- **原始數據**: 30 天
- **1 小時聚合**: 90 天 (可選)
- **1 天聚合**: 1 年 (可選)

---

## 🐛 故障排查

### 問題 1: Prometheus 無法抓取指標

**症狀**: Targets 顯示 "Down"

**解決**:
```bash
# 1. 檢查網絡連接
docker network inspect monitoring

# 2. 檢查服務是否運行
docker ps | grep mem0evomem

# 3. 檢查端口是否開放
curl http://localhost:8000/metrics
```

### 問題 2: Grafana 無法連接 Prometheus

**症狀**: "Connection refused"

**解決**:
```bash
# 1. 檢查 Prometheus 是否運行
docker logs mem0evomem-prometheus

# 2. 驗證數據源配置
# Grafana → Configuration → Data Sources → Prometheus
# URL: http://prometheus:9090

# 3. 測試連接
curl http://localhost:9090/-/healthy
```

### 問題 3: 告警未觸發

**症狀**: 滿足條件但未收到告警

**解決**:
```bash
# 1. 檢查告警規則
http://localhost:9090/alerts

# 2. 檢查 AlertManager 狀態
docker logs mem0evomem-alertmanager

# 3. 驗證告警路由
http://localhost:9093/#/alerts
```

---

## 📚 參考資源

- [Prometheus 文檔](https://prometheus.io/docs/)
- [Grafana 文檔](https://grafana.com/docs/)
- [Node Exporter](https://github.com/prometheus/node_exporter)
- [cAdvisor](https://github.com/google/cadvisor)

---

**維護者**: EvoMem Team
**許可證**: Apache 2.0
**最後更新**: 2025-11-16
