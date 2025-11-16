#!/bin/bash
#
# Mem0Evomem 自動備份腳本
#
# 功能:
# - 備份 ChromaDB 向量數據庫
# - 備份環境配置
# - 清理過期備份
#
# 使用:
#   ./scripts/backup.sh
#
# Cron 定時任務:
#   0 2 * * * /app/scripts/backup.sh >> /app/logs/backup.log 2>&1

set -e  # 遇到錯誤立即退出

# ============================================
# 配置參數
# ============================================

# 備份目錄
BACKUP_DIR="${BACKUP_DIRECTORY:-./data/backups}"
DATA_DIR="${DATA_DIRECTORY:-./data}"
LOG_DIR="${LOG_DIRECTORY:-./logs}"

# 備份保留天數
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# 時間戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================
# 函數定義
# ============================================

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 檢查目錄是否存在
check_directory() {
    if [ ! -d "$1" ]; then
        log "創建目錄: $1"
        mkdir -p "$1"
    fi
}

# ============================================
# 主備份流程
# ============================================

log "=========================================="
log "Mem0Evomem 自動備份開始"
log "=========================================="

# 檢查備份目錄
check_directory "$BACKUP_DIR"
check_directory "$LOG_DIR"

# 1. 備份 ChromaDB 向量數據庫
log "步驟 1/4: 備份 ChromaDB 數據庫"

CHROMA_DIR="$DATA_DIR/chroma_db"
CHROMA_BACKUP="$BACKUP_DIR/chroma_$TIMESTAMP.tar.gz"

if [ -d "$CHROMA_DIR" ]; then
    tar -czf "$CHROMA_BACKUP" -C "$DATA_DIR" chroma_db
    CHROMA_SIZE=$(du -sh "$CHROMA_BACKUP" | cut -f1)
    log "✅ ChromaDB 備份完成: $CHROMA_BACKUP ($CHROMA_SIZE)"
else
    warn "ChromaDB 目錄不存在: $CHROMA_DIR"
fi

# 2. 備份環境配置
log "步驟 2/4: 備份環境配置"

ENV_BACKUP="$BACKUP_DIR/env_$TIMESTAMP.backup"

if [ -f ".env" ]; then
    # 備份 .env 但移除敏感資訊 (僅保留結構)
    sed 's/=.*/=***REDACTED***/g' .env > "$ENV_BACKUP"
    log "✅ 環境配置備份完成 (敏感資訊已隱藏): $ENV_BACKUP"

    # 備份完整 .env 到安全位置 (可選)
    if [ ! -z "$SECURE_BACKUP_DIR" ]; then
        cp .env "$SECURE_BACKUP_DIR/env_$TIMESTAMP.secure"
        log "✅ 完整配置已備份到安全位置"
    fi
else
    warn ".env 文件不存在"
fi

# 3. 備份日誌 (最近 7 天)
log "步驟 3/4: 備份日誌文件"

if [ -d "$LOG_DIR" ]; then
    LOG_BACKUP="$BACKUP_DIR/logs_$TIMESTAMP.tar.gz"
    find "$LOG_DIR" -name "*.log" -mtime -7 -print0 | \
        tar -czf "$LOG_BACKUP" --null -T -

    if [ -f "$LOG_BACKUP" ]; then
        LOG_SIZE=$(du -sh "$LOG_BACKUP" | cut -f1)
        log "✅ 日誌備份完成: $LOG_BACKUP ($LOG_SIZE)"
    fi
else
    warn "日誌目錄不存在: $LOG_DIR"
fi

# 4. 清理過期備份
log "步驟 4/4: 清理過期備份 (保留 $RETENTION_DAYS 天)"

DELETED_COUNT=$(find "$BACKUP_DIR" -name "*.tar.gz" -o -name "*.backup" -mtime +$RETENTION_DAYS -delete -print | wc -l)

if [ $DELETED_COUNT -gt 0 ]; then
    log "✅ 清理完成: 刪除 $DELETED_COUNT 個過期備份"
else
    log "✅ 無需清理過期備份"
fi

# ============================================
# 備份驗證
# ============================================

log "=========================================="
log "備份驗證"
log "=========================================="

# 統計當前備份
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "*.tar.gz" -o -name "*.backup" | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

log "備份目錄: $BACKUP_DIR"
log "備份文件總數: $TOTAL_BACKUPS"
log "總大小: $TOTAL_SIZE"

# ============================================
# 生成備份清單
# ============================================

MANIFEST="$BACKUP_DIR/backup_manifest_$DATE.txt"

cat > "$MANIFEST" << EOF
Mem0Evomem 備份清單
生成時間: $(date)
備份目錄: $BACKUP_DIR

本次備份文件:
-------------------------------------------
$(if [ -f "$CHROMA_BACKUP" ]; then echo "ChromaDB: $CHROMA_BACKUP ($CHROMA_SIZE)"; fi)
$(if [ -f "$ENV_BACKUP" ]; then echo "環境配置: $ENV_BACKUP"; fi)
$(if [ -f "$LOG_BACKUP" ]; then echo "日誌: $LOG_BACKUP ($LOG_SIZE)"; fi)

備份統計:
-------------------------------------------
總備份數: $TOTAL_BACKUPS
總大小: $TOTAL_SIZE
保留天數: $RETENTION_DAYS 天

最新 10 個備份:
-------------------------------------------
$(find "$BACKUP_DIR" -name "*.tar.gz" -printf '%T+ %p\n' | sort -r | head -10)
EOF

log "✅ 備份清單已生成: $MANIFEST"

# ============================================
# 完成
# ============================================

log "=========================================="
log "✅ 備份完成！"
log "=========================================="
log "備份時間戳: $TIMESTAMP"
log "下次備份: $(date -d '+1 day' +'%Y-%m-%d 02:00:00')"

exit 0
