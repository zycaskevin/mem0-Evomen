"""簡單的導入測試"""
import sys
import os

print("=" * 60)
print("Step 1: 測試基本導入")
print("=" * 60)

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
print(f"[OK] 專案根目錄: {project_root}")

# 測試導入 src 模組
try:
    import src
    print("[OK] src 模組導入成功")
except Exception as e:
    print(f"[FAIL] src 模組導入失敗: {e}")

# 測試導入 embeddings 模組
try:
    from src import embeddings
    print("[OK] src.embeddings 模組導入成功")
except Exception as e:
    print(f"[FAIL] src.embeddings 模組導入失敗: {e}")

# 測試導入 BGEM3Embedding 類別
try:
    from src.embeddings.bge_m3 import BGEM3Embedding
    print("[OK] BGEM3Embedding 類別導入成功")
    print(f"[OK] 類別位置: {BGEM3Embedding.__module__}")
except Exception as e:
    print(f"[FAIL] BGEM3Embedding 類別導入失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Step 2: 測試依賴")
print("=" * 60)

# 測試 FlagEmbedding 導入
try:
    from FlagEmbedding import BGEM3FlagModel
    print("[OK] FlagEmbedding 導入成功")
except Exception as e:
    print(f"[FAIL] FlagEmbedding 導入失敗: {e}")

# 測試 numpy 導入
try:
    import numpy as np
    print(f"[OK] numpy 導入成功 (version {np.__version__})")
except Exception as e:
    print(f"[FAIL] numpy 導入失敗: {e}")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)
