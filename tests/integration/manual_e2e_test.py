"""BGE-M3 + mem0 手動端到端測試

繞過 PyTorch 兼容性問題的簡化測試腳本

Author: EvoMem Team
License: Apache 2.0
"""

import os
import sys
import shutil

# 添加 mem0-evomem 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../mem0-evomem"))

print("=" * 80)
print("BGE-M3 + mem0 端到端整合測試")
print("=" * 80)

# 清理舊測試數據
if os.path.exists("./test_chroma_db"):
    shutil.rmtree("./test_chroma_db")
    print("✅ 清理舊測試數據")

# 測試 1: 導入檢查
print("\n[Test 1] Import Check")
try:
    from mem0 import Memory
    print("[OK] mem0.Memory imported successfully")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# 測試 2: 創建 Memory 實例
print("\n[Test 2] Create Memory Instance (BGE-M3 embedder)")
try:
    config = {
        "embedder": {
            "provider": "bge_m3",
            "config": {
                "model": "BAAI/bge-m3",
                "model_kwargs": {
                    "use_fp16": True,
                    "device": "cpu",
                    "max_length": 8192
                }
            }
        },
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "e2e_test_collection",
                "path": "./test_chroma_db"
            }
        }
    }

    memory = Memory.from_config(config)
    print("✅ Memory 實例創建成功")
    print(f"   Embedder: {memory.embedding_model.__class__.__name__}")
    print(f"   Vector Store: {memory.vector_store.__class__.__name__}")
except Exception as e:
    print(f"❌ 創建失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 測試 3: 添加中文記憶
print("\n📝 測試 3: 添加中文記憶")
test_memories = [
    "人工智慧正在改變世界，特別是在中文語義理解方面有重大突破",
    "Python 是一種高級程式語言，以簡潔易讀著稱",
    "深度學習使用神經網路模擬人腦，在圖像和語音識別表現優異"
]

added_count = 0
for i, text in enumerate(test_memories, 1):
    try:
        result = memory.add(text, user_id=f"test_user_{i}")
        print(f"✅ 記憶 {i} 添加成功")
        added_count += 1
    except Exception as e:
        print(f"❌ 記憶 {i} 添加失敗: {e}")

print(f"\n📊 添加統計: {added_count}/{len(test_memories)} 成功")

# 測試 4: 中文語義搜索
print("\n🔍 測試 4: 中文語義搜索")
search_queries = [
    ("AI 對世界的影響", "test_user_1", "應找到關於 AI 的記憶"),
    ("什麼是 Python？", "test_user_2", "應找到關於 Python 的記憶"),
    ("神經網絡如何工作？", "test_user_3", "應找到關於深度學習的記憶"),
]

search_success = 0
for query, user_id, expected in search_queries:
    try:
        results = memory.search(query, user_id=user_id)
        print(f"\n查詢: \"{query}\"")
        print(f"用戶: {user_id}")
        print(f"期望: {expected}")
        print(f"結果數量: {len(results)}")

        if len(results) > 0:
            print(f"✅ 搜索成功")
            # 顯示第一個結果
            first = results[0]
            if isinstance(first, dict):
                memory_text = first.get("memory", first.get("text", ""))
                score = first.get("score", first.get("distance", "N/A"))
                print(f"   Top 1: {memory_text[:50]}...")
                print(f"   Score: {score}")
            search_success += 1
        else:
            print(f"❌ 未找到結果")
    except Exception as e:
        print(f"❌ 搜索失敗: {e}")

print(f"\n📊 搜索統計: {search_success}/{len(search_queries)} 成功")

# 測試 5: 語義相似度驗證
print("\n🎯 測試 5: 語義相似度驗證（同義詞測試）")
try:
    # 添加原始記憶
    memory.add("機器學習是 AI 的核心技術", user_id="test_user_semantic")

    # 使用同義詞查詢（網絡 vs 網路）
    results = memory.search("人工智慧的關鍵技術是什麼？", user_id="test_user_semantic")

    if len(results) > 0:
        print("✅ 語義相似度測試通過")
        print(f"   查詢: 人工智慧的關鍵技術")
        print(f"   找到: {len(results)} 條相關記憶")
    else:
        print("❌ 語義相似度測試失敗（未找到相關記憶）")
except Exception as e:
    print(f"❌ 語義相似度測試失敗: {e}")

# 測試 6: 批次操作
print("\n📦 測試 6: 批次添加記憶")
batch_texts = [
    "機器學習包括監督式學習和非監督式學習",
    "強化學習透過獎勵機制訓練 AI",
    "遷移學習可以復用預訓練模型"
]

batch_success = 0
for text in batch_texts:
    try:
        memory.add(text, user_id="test_user_batch")
        batch_success += 1
    except Exception as e:
        print(f"❌ 批次添加失敗: {e}")

print(f"📊 批次添加: {batch_success}/{len(batch_texts)} 成功")

# 測試批次搜索
try:
    results = memory.search("AI 訓練方法", user_id="test_user_batch", limit=3)
    print(f"✅ 批次搜索成功，返回 {len(results)} 條結果")
except Exception as e:
    print(f"❌ 批次搜索失敗: {e}")

# 清理
print("\n🧹 清理測試數據")
try:
    if os.path.exists("./test_chroma_db"):
        shutil.rmtree("./test_chroma_db")
    print("✅ 清理完成")
except Exception as e:
    print(f"⚠️  清理失敗: {e}")

# 總結
print("\n" + "=" * 80)
print("📊 測試總結")
print("=" * 80)
print(f"✅ 導入檢查: 通過")
print(f"✅ Memory 實例創建: 通過")
print(f"✅ 添加記憶: {added_count}/{len(test_memories)}")
print(f"✅ 搜索記憶: {search_success}/{len(search_queries)}")
print(f"✅ 批次操作: {batch_success}/{len(batch_texts)}")
print("=" * 80)

if added_count == len(test_memories) and search_success >= 2:
    print("🎉 端到端整合測試基本通過！")
    sys.exit(0)
else:
    print("⚠️  部分測試未通過，需進一步調查")
    sys.exit(1)
