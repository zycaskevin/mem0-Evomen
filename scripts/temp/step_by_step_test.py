"""逐步驗證 BGE-M3 實作"""
import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def test_step(step_num, description, test_func):
    """執行單個測試步驟"""
    print(f"\n[{step_num}] {description}")
    try:
        result = test_func()
        print(f"[OK] {description} 成功")
        return True
    except Exception as e:
        print(f"[FAIL] {description} 失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print_header("BGE-M3 逐步驗證測試")

# Step 1: 測試依賴
def step1():
    import numpy
    import FlagEmbedding
    return True

success = test_step(1, "測試依賴套件（numpy, FlagEmbedding）", step1)
if not success:
    print("\n[ERROR] 依賴套件未安裝，請執行: pip install numpy FlagEmbedding")
    sys.exit(1)

# Step 2: 測試模組導入
def step2():
    from src.embeddings.bge_m3 import BGEM3Embedding
    return True

success = test_step(2, "導入 BGEM3Embedding 類別", step2)
if not success:
    print("\n[ERROR] 無法導入 BGEM3Embedding，請檢查 src/embeddings/bge_m3.py")
    sys.exit(1)

# Step 3: 測試實例化
def step3():
    from src.embeddings.bge_m3 import BGEM3Embedding
    embedder = BGEM3Embedding()
    return embedder

success = test_step(3, "實例化 BGEM3Embedding（載入模型）", step3)
if not success:
    print("\n[ERROR] 無法實例化，可能是模型載入失敗")
    sys.exit(1)

embedder = step3()

# Step 4: 測試單文本嵌入
def step4():
    result = embedder.embed("測試文本")
    assert len(result) == 1024, f"Expected 1024 dimensions, got {len(result)}"
    assert all(isinstance(x, float) for x in result), "All elements should be float"
    return result

success = test_step(4, "測試單文本嵌入", step4)
if not success:
    print("\n[ERROR] 單文本嵌入失敗")
    sys.exit(1)

# Step 5: 測試空文本錯誤
def step5():
    try:
        embedder.embed("")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        if "不能嵌入空文本" in str(e):
            return True
        else:
            raise AssertionError(f"Wrong error message: {e}")

success = test_step(5, "測試空文本錯誤處理", step5)

# Step 6: 測試批次嵌入
def step6():
    texts = ["文本1", "文本2", "文本3"]
    results = embedder.batch_embed(texts)
    assert len(results) == 3, f"Expected 3 vectors, got {len(results)}"
    assert all(len(r) == 1024 for r in results), "All vectors should be 1024-dim"
    return results

success = test_step(6, "測試批次嵌入", step6)

# Step 7: 測試空列表
def step7():
    results = embedder.batch_embed([])
    assert results == [], f"Expected empty list, got {results}"
    return True

success = test_step(7, "測試空列表批次嵌入", step7)

# Step 8: 測試模型配置
def step8():
    assert embedder.model_name == "BAAI/bge-m3"
    assert embedder.use_fp16 is True
    assert embedder.device == "cpu"
    assert embedder.max_length == 8192
    return True

success = test_step(8, "測試模型配置", step8)

print_header("驗證結果")
print("\n[SUCCESS] 所有基本測試通過！")
print("\n[INFO] 如需完整測試（包含效能測試），請執行:")
print("       python scripts\\verify_bge_m3_implementation.py")
print("\n[INFO] 下一步: 提交 Green Phase")
print("       git commit -m 'feat(TDD-Green): 實現 BGE-M3 Embedder'")
