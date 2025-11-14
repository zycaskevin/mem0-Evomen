"""BGE-M3 Embedder 單元測試 - TDD Red Phase

測試基於 features/bge_m3.feature 的 BDD 規格
按照 CLAUDE.md 的 TDD 工作流程：Phase 1 Red - 先寫測試
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import threading
import time


class TestBGEM3Embedding:
    """BGE-M3 Embedder 核心功能測試"""

    def test_embed_returns_1024_dimensions(self):
        """
        Scenario: 嵌入單個中文文本
        Given 一個 BGEM3Embedding 實例
        When 我嵌入文本 "這是一個測試句子"
        Then 應該返回一個 1024 維的向量
        And 向量的每個元素都是浮點數
        And 向量的每個元素範圍在 [-1, 1] 之間
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()
        result = embedder.embed("這是一個測試句子")

        # 驗證維度
        assert len(result) == 1024, f"Expected 1024 dimensions, got {len(result)}"

        # 驗證元素類型
        assert all(isinstance(x, (float, np.floating)) for x in result), \
            "All elements should be float"

        # 驗證元素範圍
        assert all(-1 <= x <= 1 for x in result), \
            "All elements should be in range [-1, 1]"

    def test_embed_empty_text_raises_error(self):
        """
        Scenario: 嵌入空文本應該拋出錯誤
        Given 一個 BGEM3Embedding 實例
        When 我嵌入空文本 ""
        Then 應該拋出 ValueError 異常
        And 異常訊息應該包含 "不能嵌入空文本"
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        with pytest.raises(ValueError, match="不能嵌入空文本"):
            embedder.embed("")

    def test_embed_long_text_truncates(self, caplog):
        """
        Scenario: 嵌入超長文本應該自動截斷
        Given 一個 BGEM3Embedding 實例
        When 我嵌入一個超過 8192 token 的長文本
        Then 應該自動截斷到 8192 token
        And 應該返回一個 1024 維的向量
        And 應該記錄警告訊息
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        # 創建超長文本（約 10000 個字，遠超 8192 token）
        long_text = "人工智慧技術正在快速發展。" * 2000

        result = embedder.embed(long_text)

        # 驗證返回 1024 維向量
        assert len(result) == 1024

        # 驗證警告訊息
        assert any("截斷" in record.message or "truncate" in record.message.lower()
                   for record in caplog.records), \
            "Should log warning about truncation"

    def test_batch_embed(self):
        """
        Scenario: 批次嵌入多個文本
        Given 一個 BGEM3Embedding 實例
        When 我批次嵌入以下文本：
          | 文本                     |
          | 人工智慧正在改變世界       |
          | 機器學習是 AI 的核心技術   |
          | 深度學習推動了 AI 的發展   |
        Then 應該返回一個包含 3 個向量的列表
        And 每個向量都是 1024 維
        And 所有向量的元素都是浮點數
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        texts = [
            "人工智慧正在改變世界",
            "機器學習是 AI 的核心技術",
            "深度學習推動了 AI 的發展"
        ]

        results = embedder.batch_embed(texts)

        # 驗證返回 3 個向量
        assert len(results) == 3

        # 驗證每個向量都是 1024 維
        for result in results:
            assert len(result) == 1024

        # 驗證所有元素都是浮點數
        for result in results:
            assert all(isinstance(x, (float, np.floating)) for x in result)

    def test_batch_embed_empty_list(self):
        """
        Scenario: 批次嵌入空列表應該返回空列表
        Given 一個 BGEM3Embedding 實例
        When 我批次嵌入一個空列表
        Then 應該返回一個空列表
        And 不應該拋出任何異常
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        results = embedder.batch_embed([])

        assert results == []

    def test_similar_texts_high_similarity(self):
        """
        Scenario: 相似文本應該有相似的向量
        Given 一個 BGEM3Embedding 實例
        When 我嵌入文本 "人工智慧"
        And 我嵌入文本 "AI 技術"
        Then 兩個向量的餘弦相似度應該大於 0.7
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        vec1 = embedder.embed("人工智慧")
        vec2 = embedder.embed("AI 技術")

        # 計算餘弦相似度
        similarity = self._cosine_similarity(vec1, vec2)

        assert similarity > 0.7, \
            f"Expected similarity > 0.7 for similar texts, got {similarity}"

    def test_dissimilar_texts_low_similarity(self):
        """
        Scenario: 不相似文本應該有不同的向量
        Given 一個 BGEM3Embedding 實例
        When 我嵌入文本 "人工智慧"
        And 我嵌入文本 "今天天氣很好"
        Then 兩個向量的餘弦相似度應該小於 0.5
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        vec1 = embedder.embed("人工智慧")
        vec2 = embedder.embed("今天天氣很好")

        # 計算餘弦相似度
        similarity = self._cosine_similarity(vec1, vec2)

        assert similarity < 0.5, \
            f"Expected similarity < 0.5 for dissimilar texts, got {similarity}"

    @pytest.mark.parametrize("char_count", [5, 50, 500, 2000])
    def test_embed_different_lengths(self, char_count):
        """
        Scenario Outline: 嵌入不同長度的文本
        Given 一個 BGEM3Embedding 實例
        When 我嵌入一個包含 <字數> 個字的文本
        Then 應該返回一個 1024 維的向量
        And 向量的每個元素都是浮點數

        Examples: 文本長度
          | 字數 |
          | 5    |
          | 50   |
          | 500  |
          | 2000 |
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        # 創建指定長度的文本
        text = "測" * char_count

        result = embedder.embed(text)

        # 驗證維度
        assert len(result) == 1024

        # 驗證元素類型
        assert all(isinstance(x, (float, np.floating)) for x in result)

    def test_model_configuration(self):
        """
        Scenario: 驗證模型配置
        Given 一個 BGEM3Embedding 實例
        Then 模型名稱應該是 "BAAI/bge-m3"
        And 應該使用 FP16 精度
        And 應該運行在 CPU 上
        And 最大序列長度應該是 8192
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        # 驗證模型名稱
        assert embedder.model_name == "BAAI/bge-m3"

        # 驗證 FP16 精度
        assert embedder.use_fp16 is True

        # 驗證設備（CPU）
        assert embedder.device == "cpu"

        # 驗證最大序列長度
        assert embedder.max_length == 8192

    def test_concurrent_embedding(self):
        """
        Scenario: 多線程並發嵌入
        Given 一個 BGEM3Embedding 實例
        When 我在 4 個線程中同時嵌入不同的文本
        Then 所有嵌入操作都應該成功
        And 返回的向量應該是確定性的（相同文本總是返回相同向量）
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        texts = [
            "人工智慧",
            "機器學習",
            "深度學習",
            "自然語言處理"
        ]

        results = {}

        def embed_text(text):
            results[text] = embedder.embed(text)

        # 創建 4 個線程
        threads = [threading.Thread(target=embed_text, args=(text,))
                   for text in texts]

        # 啟動所有線程
        for thread in threads:
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()

        # 驗證所有文本都成功嵌入
        assert len(results) == 4

        # 驗證確定性（同一文本多次嵌入結果相同）
        for text in texts:
            vec1 = results[text]
            vec2 = embedder.embed(text)

            # 使用 numpy.allclose 檢查向量是否相同（允許浮點誤差）
            assert np.allclose(vec1, vec2, rtol=1e-5), \
                f"Text '{text}' should produce deterministic embeddings"

    def test_memory_performance(self):
        """
        Scenario: 記憶體效能驗證
        Given 一個 BGEM3Embedding 實例
        When 我批次嵌入 100 個文本
        Then 記憶體使用量不應該超過 2GB
        And 所有嵌入操作都應該在 30 秒內完成
        """
        from src.embeddings.bge_m3 import BGEM3Embedding
        import psutil
        import os

        embedder = BGEM3Embedding()

        # 準備 100 個測試文本
        texts = [f"這是第 {i} 個測試文本，用於驗證記憶體效能。" for i in range(100)]

        # 記錄開始時間和記憶體
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / (1024 ** 3)  # GB

        # 執行批次嵌入
        results = embedder.batch_embed(texts)

        # 記錄結束時間和記憶體
        end_time = time.time()
        end_memory = process.memory_info().rss / (1024 ** 3)  # GB

        elapsed_time = end_time - start_time
        memory_used = end_memory - start_memory

        # 驗證所有嵌入成功
        assert len(results) == 100

        # 驗證時間效能（30 秒內完成）
        assert elapsed_time < 30, \
            f"Expected < 30s, took {elapsed_time:.2f}s"

        # 驗證記憶體效能（不超過 2GB）
        assert memory_used < 2.0, \
            f"Expected < 2GB memory usage, used {memory_used:.2f}GB"

    @pytest.mark.performance
    def test_batch_processing_performance(self):
        """
        Scenario: 批次處理效能優化
        Given 一個 BGEM3Embedding 實例
        When 我使用 batch_size=256 批次嵌入 1000 個文本
        Then 平均每個文本的嵌入時間應該小於 50ms
        And 批次處理應該比逐個處理快至少 5 倍
        """
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        # 準備 1000 個測試文本（使用較短文本以加快測試速度）
        texts = [f"測試文本 {i}" for i in range(1000)]

        # 測試批次處理時間
        start_batch = time.time()
        batch_results = embedder.batch_embed(texts, batch_size=256)
        batch_time = time.time() - start_batch

        # 測試逐個處理時間（只測試前 100 個以節省時間）
        start_single = time.time()
        for text in texts[:100]:
            embedder.embed(text)
        single_time = (time.time() - start_single) * 10  # 估算 1000 個的時間

        # 驗證批次處理成功
        assert len(batch_results) == 1000

        # 驗證平均時間（50ms per text）
        avg_time_ms = (batch_time / 1000) * 1000
        assert avg_time_ms < 50, \
            f"Expected < 50ms per text, got {avg_time_ms:.2f}ms"

        # 驗證批次處理比逐個處理快至少 5 倍
        speedup = single_time / batch_time
        assert speedup >= 5, \
            f"Expected batch processing ≥5x faster, got {speedup:.2f}x"

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        """計算餘弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        return dot_product / (norm1 * norm2)


class TestBGEM3EmbeddingEdgeCases:
    """BGE-M3 Embedder 邊界情況測試"""

    def test_embed_special_characters(self):
        """測試特殊字元嵌入"""
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        # 測試 emoji
        result = embedder.embed("這是測試 😀 🎉")
        assert len(result) == 1024

        # 測試標點符號
        result = embedder.embed("！@#$%^&*（）【】")
        assert len(result) == 1024

    def test_embed_mixed_language(self):
        """測試中英混合文本"""
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        result = embedder.embed("人工智慧 Artificial Intelligence AI")
        assert len(result) == 1024

    def test_embed_numbers_only(self):
        """測試純數字文本"""
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        result = embedder.embed("123456789")
        assert len(result) == 1024

    def test_batch_embed_with_duplicates(self):
        """測試批次嵌入包含重複文本"""
        from src.embeddings.bge_m3 import BGEM3Embedding

        embedder = BGEM3Embedding()

        texts = ["測試", "測試", "不同"]
        results = embedder.batch_embed(texts)

        # 驗證返回 3 個向量
        assert len(results) == 3

        # 驗證前兩個向量相同（確定性）
        assert np.allclose(results[0], results[1], rtol=1e-5)

        # 驗證第三個向量不同
        similarity = np.dot(results[0], results[2]) / \
                     (np.linalg.norm(results[0]) * np.linalg.norm(results[2]))
        assert similarity < 0.99  # 不完全相同
