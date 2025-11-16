"""驗證 BGE-M3 Embedder 實作

手動驗證實作符合測試規格，避免 pytest 的環境問題
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_embed_returns_1024_dimensions():
    """測試單個文本嵌入返回 1024 維向量"""
    print("[INFO] 測試 1/13: embed() 返回 1024 維向量")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()
    result = embedder.embed("這是一個測試句子")

    assert len(result) == 1024, f"Expected 1024 dimensions, got {len(result)}"
    assert all(isinstance(x, float) for x in result), "All elements should be float"
    assert all(-1 <= x <= 1 for x in result), "All elements should be in range [-1, 1]"

    print("[OK] 測試通過")


def test_embed_empty_text_raises_error():
    """測試空文本應該拋出 ValueError"""
    print("[INFO] 測試 2/13: 空文本拋出 ValueError")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    try:
        embedder.embed("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "不能嵌入空文本" in str(e)
        print("[OK] 測試通過")


def test_batch_embed():
    """測試批次嵌入多個文本"""
    print("[INFO] 測試 3/13: batch_embed() 批次嵌入")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    texts = [
        "人工智慧正在改變世界",
        "機器學習是 AI 的核心技術",
        "深度學習推動了 AI 的發展"
    ]

    results = embedder.batch_embed(texts)

    assert len(results) == 3, f"Expected 3 vectors, got {len(results)}"
    assert all(len(result) == 1024 for result in results), "All vectors should be 1024-dim"

    print("[OK] 測試通過")


def test_batch_embed_empty_list():
    """測試批次嵌入空列表"""
    print("[INFO] 測試 4/13: batch_embed([]) 返回空列表")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()
    results = embedder.batch_embed([])

    assert results == [], f"Expected empty list, got {results}"

    print("[OK] 測試通過")


def test_similar_texts_high_similarity():
    """測試相似文本有相似的向量"""
    print("[INFO] 測試 5/13: 相似文本高相似度")

    import numpy as np
    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    vec1 = embedder.embed("人工智慧")
    vec2 = embedder.embed("AI 技術")

    # 計算餘弦相似度
    vec1_arr = np.array(vec1)
    vec2_arr = np.array(vec2)
    similarity = np.dot(vec1_arr, vec2_arr) / (
        np.linalg.norm(vec1_arr) * np.linalg.norm(vec2_arr)
    )

    print(f"   - 相似度: {similarity:.4f}")
    assert similarity > 0.7, f"Expected similarity > 0.7, got {similarity}"

    print("[OK] 測試通過")


def test_model_configuration():
    """測試模型配置"""
    print("[INFO] 測試 6/13: 模型配置驗證")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    assert embedder.model_name == "BAAI/bge-m3"
    assert embedder.use_fp16 is True
    assert embedder.device == "cpu"
    assert embedder.max_length == 8192

    print("[OK] 測試通過")


def test_embed_different_lengths():
    """測試不同長度的文本"""
    print("[INFO] 測試 7/13: 不同長度文本嵌入")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    for char_count in [5, 50, 500]:
        text = "測" * char_count
        result = embedder.embed(text)
        assert len(result) == 1024, f"Failed for length {char_count}"

    print("[OK] 測試通過")


def test_deterministic_embedding():
    """測試確定性嵌入（相同文本總是返回相同向量）"""
    print("[INFO] 測試 8/13: 確定性嵌入")

    import numpy as np
    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    text = "測試文本"
    vec1 = embedder.embed(text)
    vec2 = embedder.embed(text)

    assert np.allclose(vec1, vec2, rtol=1e-5), "Same text should produce same embeddings"

    print("[OK] 測試通過")


def test_special_characters():
    """測試特殊字元"""
    print("[INFO] 測試 9/13: 特殊字元處理")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    # 測試 emoji
    result = embedder.embed("這是測試 😀 🎉")
    assert len(result) == 1024

    # 測試標點符號
    result = embedder.embed("！@#$%^&*（）【】")
    assert len(result) == 1024

    print("[OK] 測試通過")


def test_mixed_language():
    """測試中英混合文本"""
    print("[INFO] 測試 10/13: 中英混合文本")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    result = embedder.embed("人工智慧 Artificial Intelligence AI")
    assert len(result) == 1024

    print("[OK] 測試通過")


def test_batch_with_duplicates():
    """測試批次嵌入包含重複文本"""
    print("[INFO] 測試 11/13: 批次嵌入重複文本")

    import numpy as np
    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    texts = ["測試", "測試", "不同"]
    results = embedder.batch_embed(texts)

    assert len(results) == 3
    assert np.allclose(results[0], results[1], rtol=1e-5), "Duplicate texts should have same embeddings"

    print("[OK] 測試通過")


def test_long_text_warning():
    """測試超長文本警告"""
    print("[INFO] 測試 12/13: 超長文本警告")

    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    # 創建超長文本（約 10000 字）
    long_text = "人工智慧技術正在快速發展。" * 800

    result = embedder.embed(long_text)
    assert len(result) == 1024

    print("[OK] 測試通過（檢查上方是否有警告訊息）")


def test_dissimilar_texts_low_similarity():
    """測試不相似文本低相似度"""
    print("[INFO] 測試 13/13: 不相似文本低相似度")

    import numpy as np
    from src.embeddings.bge_m3 import BGEM3Embedding

    embedder = BGEM3Embedding()

    vec1 = embedder.embed("人工智慧")
    vec2 = embedder.embed("今天天氣很好")

    # 計算餘弦相似度
    vec1_arr = np.array(vec1)
    vec2_arr = np.array(vec2)
    similarity = np.dot(vec1_arr, vec2_arr) / (
        np.linalg.norm(vec1_arr) * np.linalg.norm(vec2_arr)
    )

    print(f"   - 相似度: {similarity:.4f}")
    assert similarity < 0.5, f"Expected similarity < 0.5, got {similarity}"

    print("[OK] 測試通過")


def main():
    """運行所有驗證測試"""
    print("=" * 60)
    print("BGE-M3 Embedder 實作驗證")
    print("=" * 60)
    print()

    tests = [
        test_embed_returns_1024_dimensions,
        test_embed_empty_text_raises_error,
        test_batch_embed,
        test_batch_embed_empty_list,
        test_similar_texts_high_similarity,
        test_model_configuration,
        test_embed_different_lengths,
        test_deterministic_embedding,
        test_special_characters,
        test_mixed_language,
        test_batch_with_duplicates,
        test_long_text_warning,
        test_dissimilar_texts_low_similarity,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
            print()
        except Exception as e:
            print(f"[FAIL] {e}")
            print()
            failed += 1

    print("=" * 60)
    print("驗證結果")
    print("=" * 60)
    print(f"通過: {passed}/{len(tests)}")
    print(f"失敗: {failed}/{len(tests)}")

    if failed == 0:
        print()
        print("[SUCCESS] 所有驗證測試通過！")
        print()
        print("[=>] 下一步:")
        print("1. 提交 Green Phase 實作: git commit -m 'feat(TDD-Green): 實現 BGE-M3 Embedder'")
        print("2. 開始 Refactor Phase: 優化效能、錯誤處理、文檔")
        return 0
    else:
        print()
        print("[ERROR] 部分測試失敗，請修復後重新驗證")
        return 1


if __name__ == "__main__":
    sys.exit(main())
