"""BGE-M3 + mem0 端到端整合測試

測試場景:
1. 基本記憶添加與搜索
2. 中文語義相似度搜索
3. 批次記憶管理
4. memory_action 參數驗證

Author: EvoMem Team
License: Apache 2.0
"""

import os
import sys
import pytest
import shutil
from typing import List, Dict, Any

# 添加 mem0-evomem 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../mem0-evomem"))

from mem0 import Memory


@pytest.fixture(scope="module")
def memory_instance():
    """創建 Memory 實例（使用 BGE-M3 embedder）"""
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
    yield memory

    # 清理測試數據
    if os.path.exists("./test_chroma_db"):
        shutil.rmtree("./test_chroma_db")


class TestBasicMemoryOperations:
    """測試基本記憶操作"""

    def test_add_single_memory(self, memory_instance):
        """測試添加單個記憶"""
        result = memory_instance.add(
            "人工智慧正在改變世界，特別是在中文語義理解方面有重大突破",
            user_id="user_001"
        )

        assert result is not None
        assert "results" in result or "id" in result

    def test_search_memory(self, memory_instance):
        """測試搜索記憶"""
        # 添加記憶
        memory_instance.add(
            "Python 是一種高級程式語言，以簡潔易讀著稱",
            user_id="user_002"
        )

        # 搜索記憶
        results = memory_instance.search(
            "什麼是 Python？",
            user_id="user_002"
        )

        assert isinstance(results, list)
        assert len(results) > 0
        assert "memory" in results[0] or "text" in results[0]


class TestChineseSemanticSearch:
    """測試中文語義搜索準確度"""

    def test_synonym_search(self, memory_instance):
        """測試同義詞搜索"""
        # 添加原始記憶
        memory_instance.add(
            "深度學習使用神經網路模擬人腦",
            user_id="user_003"
        )

        # 使用同義詞搜索
        results = memory_instance.search(
            "神經網絡如何工作？",  # 網絡 vs 網路
            user_id="user_003"
        )

        assert len(results) > 0
        # 驗證返回的記憶包含相關內容
        found = any("神經網" in str(r.get("memory", "")) for r in results)
        assert found, "應該找到包含同義詞的記憶"

    def test_semantic_similarity(self, memory_instance):
        """測試語義相似度（非字面匹配）"""
        # 添加記憶
        memory_instance.add(
            "機器學習是 AI 的核心技術",
            user_id="user_004"
        )

        # 使用語義相似但不同詞彙的查詢
        results = memory_instance.search(
            "人工智慧的關鍵技術是什麼？",
            user_id="user_004"
        )

        assert len(results) > 0

    def test_chinese_english_mixed(self, memory_instance):
        """測試中英混合文本"""
        # 添加中英混合記憶
        memory_instance.add(
            "TDD (Test-Driven Development) 是一種軟體開發方法",
            user_id="user_005"
        )

        # 搜索
        results = memory_instance.search(
            "什麼是測試驅動開發？",
            user_id="user_005"
        )

        assert len(results) > 0


class TestBatchMemoryManagement:
    """測試批次記憶管理"""

    def test_add_multiple_memories(self, memory_instance):
        """測試批次添加多個記憶"""
        texts = [
            "機器學習包括監督式學習和非監督式學習",
            "強化學習透過獎勵機制訓練 AI",
            "遷移學習可以復用預訓練模型"
        ]

        for text in texts:
            result = memory_instance.add(text, user_id="user_006")
            assert result is not None

    def test_search_returns_top_k(self, memory_instance):
        """測試搜索返回 Top-K 結果"""
        # 搜索（應該返回最多 3 個結果）
        results = memory_instance.search(
            "AI 訓練方法",
            user_id="user_006",
            limit=3
        )

        assert isinstance(results, list)
        assert len(results) <= 3


class TestMemoryActionParameter:
    """測試 memory_action 參數"""

    def test_add_action(self, memory_instance):
        """測試 add action"""
        # 注意：當前版本 memory_action 可能在 Memory 層面不直接暴露
        # 這裡測試基本的 add 操作
        result = memory_instance.add(
            "這是一條測試記憶（add action）",
            user_id="user_007"
        )

        assert result is not None

    def test_search_action(self, memory_instance):
        """測試 search action"""
        # 添加記憶
        memory_instance.add(
            "這是一條測試記憶（search action）",
            user_id="user_008"
        )

        # 搜索
        results = memory_instance.search(
            "測試記憶",
            user_id="user_008"
        )

        assert len(results) > 0


class TestEdgeCases:
    """測試邊界情況"""

    def test_long_text_memory(self, memory_instance):
        """測試長文本記憶"""
        long_text = "人工智慧" + "的應用包括自然語言處理、計算機視覺、語音識別" * 50

        result = memory_instance.add(long_text, user_id="user_009")
        assert result is not None

        # 搜索長文本記憶
        results = memory_instance.search("人工智慧的應用", user_id="user_009")
        assert len(results) > 0

    def test_special_characters(self, memory_instance):
        """測試特殊字符"""
        text = "Python 列表推導式：[x**2 for x in range(10)]"

        result = memory_instance.add(text, user_id="user_010")
        assert result is not None

        results = memory_instance.search("列表推導式", user_id="user_010")
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
