#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""簡單的導入測試腳本"""

import sys
import traceback

# 配置輸出編碼
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("依賴導入測試")
print("=" * 60)

# 測試 mem0
print("\n[1/5] 測試 mem0 導入...")
try:
    import mem0
    version = getattr(mem0, '__version__', 'unknown')
    print(f"✓ mem0 {version} 導入成功")
except Exception as e:
    print(f"✗ mem0 導入失敗: {e}")
    traceback.print_exc()

# 測試 FlagEmbedding 基礎導入
print("\n[2/5] 測試 FlagEmbedding 基礎導入...")
try:
    import FlagEmbedding
    print("✓ FlagEmbedding 基礎導入成功")
except Exception as e:
    print(f"✗ FlagEmbedding 基礎導入失敗: {e}")
    traceback.print_exc()

# 測試 BGEM3FlagModel
print("\n[3/5] 測試 BGEM3FlagModel 導入...")
try:
    from FlagEmbedding import BGEM3FlagModel
    print("✓ BGEM3FlagModel 導入成功")
except Exception as e:
    print(f"✗ BGEM3FlagModel 導入失敗: {e}")
    traceback.print_exc()

# 測試其他必要依賴
print("\n[4/5] 測試 torch 導入...")
try:
    import torch
    print(f"✓ torch {torch.__version__} 導入成功")
except Exception as e:
    print(f"✗ torch 導入失敗: {e}")

print("\n[5/5] 測試 transformers 導入...")
try:
    import transformers
    print(f"✓ transformers {transformers.__version__} 導入成功")
except Exception as e:
    print(f"✗ transformers 導入失敗: {e}")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)
