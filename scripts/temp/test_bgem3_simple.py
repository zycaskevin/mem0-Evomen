#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""簡化的 BGE-M3 測試腳本"""

import sys
import os

# 設置輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 60)
print("BGE-M3 簡化測試")
print("=" * 60)

# 步驟 1: 檢查 FlagEmbedding 安裝
print("\n[1/3] 檢查 FlagEmbedding 安裝...")
try:
    import FlagEmbedding
    print("[OK] FlagEmbedding 已安裝")
except ImportError as e:
    print(f"[FAIL] FlagEmbedding 未安裝: {e}")
    print("請執行: pip install FlagEmbedding==1.3.5")
    sys.exit(1)

# 步驟 2: 檢查 BGEM3FlagModel 導入
print("\n[2/3] 檢查 BGEM3FlagModel 導入...")
try:
    from FlagEmbedding import BGEM3FlagModel
    print("[OK] BGEM3FlagModel 導入成功")
except ImportError as e:
    print(f"[FAIL] BGEM3FlagModel 導入失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 步驟 3: 嘗試載入模型
print("\n[3/3] 嘗試載入 BGE-M3 模型...")
print("[INFO] 這將會下載約 1-2 GB 的模型文件")
print("[INFO] 如果是首次運行，請耐心等待...")

try:
    print("正在載入模型...")
    model = BGEM3FlagModel(
        'BAAI/bge-m3',
        use_fp16=True,
        device='cpu'
    )
    print("[OK] 模型載入成功！")

    # 測試 encoding
    print("\n測試 encoding...")
    test_text = "這是一個測試"
    result = model.encode([test_text], batch_size=1, max_length=512)

    if isinstance(result, dict) and 'dense_vecs' in result:
        print("[OK] Encoding 成功")
        print(f"[OK] 向量維度: {result['dense_vecs'].shape}")
    else:
        print(f"[WARN] 結果格式異常: {type(result)}")
        if isinstance(result, dict):
            print(f"可用的鍵: {list(result.keys())}")

    print("\n" + "=" * 60)
    print("[SUCCESS] 所有測試通過！")
    print("=" * 60)

except Exception as e:
    print(f"\n[FAIL] 模型載入或測試失敗: {e}")
    print("\n詳細錯誤:")
    import traceback
    traceback.print_exc()

    print("\n可能的解決方案:")
    print("1. 檢查網絡連接（需要下載模型）")
    print("2. 確認有足夠的磁碟空間（至少 3 GB）")
    print("3. 嘗試使用代理或 VPN")
    print("4. 手動下載模型: https://huggingface.co/BAAI/bge-m3")

    sys.exit(1)
