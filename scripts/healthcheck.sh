#!/bin/bash
#
# Mem0Evomem 健康檢查腳本
#
# 用於 Docker healthcheck 和監控系統

set -e

# 配置
HOST="${HEALTH_CHECK_HOST:-localhost}"
PORT="${HEALTH_CHECK_PORT:-8000}"
TIMEOUT=5

# 檢查 HTTP 響應
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT http://$HOST:$PORT/health || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Health check passed"
        exit 0
    else
        echo "❌ Health check failed (HTTP $HTTP_CODE)"
        exit 1
    fi
else
    # 如果 curl 不可用，使用 Python
    python3 -c "
import urllib.request
import sys

try:
    with urllib.request.urlopen('http://$HOST:$PORT/health', timeout=$TIMEOUT) as response:
        if response.status == 200:
            print('✅ Health check passed')
            sys.exit(0)
        else:
            print(f'❌ Health check failed (HTTP {response.status})')
            sys.exit(1)
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
"
fi
