#!/bin/bash
#
# Mem0Evomem 數據恢復腳本
#
# 功能:
# - 從備份恢復 ChromaDB 數據庫
# - 恢復環境配置
# - 驗證恢復結果
#
# 使用:
#   ./scripts/restore.sh <backup_file>
#   ./scripts/restore.sh ./data/backups/chroma_20251116_140530.tar.gz

set -e  # 遇到錯誤立即退出

# ============================================
# 配置參數
# ============================================

BACKUP_FILE="$1"
DATA_DIR="${DATA_DIRECTORY:-./data}"
LOG_DIR="${LOG_DIRECTORY:-./logs}"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 顯示使用說明
show_usage() {
    cat << EOF
使用方法:
    $0 <backup_file>

參數:
    backup_file    備份文件路徑 (*.tar.gz)

範例:
    $0 ./data/backups/chroma_20251116_140530.tar.gz

可用備份列表:
$(find ./data/backups -name "chroma_*.tar.gz" -printf '  %T+ %p\n' | sort -r | head -5)
EOF
    exit 1
}

# 確認操作
confirm() {
    echo -e "${YELLOW}⚠️  警告: 此操作將覆蓋現有數據！${NC}"
    echo -e "${YELLOW}⚠️  請確認您已備份當前數據！${NC}"
    echo ""
    read -p "確定要繼續嗎？ (yes/no): " -n 3 -r
    echo
    if [[ ! $REPLY =~ ^yes$ ]]; then
        echo "操作已取消"
        exit 0
    fi
}

# ============================================
# 參數驗證
# ============================================

if [ -z "$BACKUP_FILE" ]; then
    error "缺少備份文件參數"
    show_usage
fi

if [ ! -f "$BACKUP_FILE" ]; then
    error "備份文件不存在: $BACKUP_FILE"
fi

# ============================================
# 恢復流程
# ============================================

log "=========================================="
log "Mem0Evomem 數據恢復"
log "=========================================="

info "備份文件: $BACKUP_FILE"
info "數據目錄: $DATA_DIR"
info "恢復時間: $(date)"

# 確認操作
confirm

# 1. 停止服務
log "步驟 1/5: 停止 Docker 服務"

if command -v docker-compose &> /dev/null; then
    if docker-compose ps | grep -q "Up"; then
        log "正在停止服務..."
        docker-compose down
        log "✅ 服務已停止"
    else
        info "服務未運行"
    fi
else
    warn "docker-compose 未安裝，跳過服務停止"
fi

# 2. 備份當前數據 (作為安全措施)
log "步驟 2/5: 備份當前數據"

SAFETY_BACKUP="$DATA_DIR/safety_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

if [ -d "$DATA_DIR/chroma_db" ]; then
    tar -czf "$SAFETY_BACKUP" -C "$DATA_DIR" chroma_db
    SAFETY_SIZE=$(du -sh "$SAFETY_BACKUP" | cut -f1)
    log "✅ 當前數據已備份: $SAFETY_BACKUP ($SAFETY_SIZE)"
else
    info "當前無 ChromaDB 數據"
fi

# 3. 清理現有數據
log "步驟 3/5: 清理現有數據"

if [ -d "$DATA_DIR/chroma_db" ]; then
    rm -rf "$DATA_DIR/chroma_db"
    log "✅ 現有 ChromaDB 數據已清理"
fi

# 4. 恢復數據
log "步驟 4/5: 恢復數據"

log "解壓備份文件..."
tar -xzf "$BACKUP_FILE" -C "$DATA_DIR"

if [ -d "$DATA_DIR/chroma_db" ]; then
    RESTORED_SIZE=$(du -sh "$DATA_DIR/chroma_db" | cut -f1)
    log "✅ ChromaDB 數據已恢復 ($RESTORED_SIZE)"
else
    error "恢復失敗: ChromaDB 目錄未創建"
fi

# 5. 驗證恢復
log "步驟 5/5: 驗證恢復"

# 檢查目錄結構
if [ -f "$DATA_DIR/chroma_db/chroma.sqlite3" ]; then
    log "✅ ChromaDB SQLite 數據庫存在"
else
    warn "ChromaDB SQLite 數據庫文件未找到"
fi

# 統計恢復的數據
COLLECTION_COUNT=$(find "$DATA_DIR/chroma_db" -type d -name "*collection*" | wc -l)
FILE_COUNT=$(find "$DATA_DIR/chroma_db" -type f | wc -l)

log "恢復統計:"
log "  - 集合數量: $COLLECTION_COUNT"
log "  - 文件數量: $FILE_COUNT"
log "  - 總大小: $RESTORED_SIZE"

# ============================================
# 重啟服務
# ============================================

log "=========================================="
log "重啟服務"
log "=========================================="

if command -v docker-compose &> /dev/null; then
    log "正在啟動服務..."
    docker-compose up -d
    log "✅ 服務已啟動"

    # 等待服務就緒
    log "等待服務就緒 (30 秒)..."
    sleep 30

    # 檢查服務狀態
    if docker-compose ps | grep -q "Up"; then
        log "✅ 服務運行正常"
    else
        error "服務啟動失敗，請檢查日誌"
    fi
else
    warn "docker-compose 未安裝，需要手動重啟服務"
fi

# ============================================
# 生成恢復報告
# ============================================

RESTORE_REPORT="$LOG_DIR/restore_report_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p "$LOG_DIR"

cat > "$RESTORE_REPORT" << EOF
Mem0Evomem 恢復報告
========================================

恢復時間: $(date)
備份文件: $BACKUP_FILE
數據目錄: $DATA_DIR

恢復統計:
----------------------------------------
集合數量: $COLLECTION_COUNT
文件數量: $FILE_COUNT
總大小: $RESTORED_SIZE

安全備份:
----------------------------------------
位置: $SAFETY_BACKUP
大小: $SAFETY_SIZE

驗證結果:
----------------------------------------
$(if [ -f "$DATA_DIR/chroma_db/chroma.sqlite3" ]; then echo "✅ ChromaDB 數據庫正常"; else echo "❌ ChromaDB 數據庫缺失"; fi)
$(if docker-compose ps | grep -q "Up"; then echo "✅ 服務運行正常"; else echo "❌ 服務未運行"; fi)

目錄結構:
----------------------------------------
$(tree -L 2 "$DATA_DIR/chroma_db" 2>/dev/null || find "$DATA_DIR/chroma_db" -maxdepth 2 -type d)
EOF

log "✅ 恢復報告已生成: $RESTORE_REPORT"

# ============================================
# 完成
# ============================================

log "=========================================="
log "✅ 恢復完成！"
log "=========================================="
log "備份文件: $BACKUP_FILE"
log "恢復數據: $RESTORED_SIZE"
log "安全備份: $SAFETY_BACKUP"
log "恢復報告: $RESTORE_REPORT"
log ""
info "建議:"
info "1. 檢查服務日誌確認運行正常"
info "2. 運行測試驗證數據完整性"
info "3. 保留安全備份至少 7 天"

exit 0
