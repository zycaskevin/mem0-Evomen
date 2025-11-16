"""簡單的 BGE-M3 驗證腳本 - 輸出到文件"""
import sys
import os

# 設置輸出文件
output_file = os.path.join(os.path.dirname(__file__), "test_result.txt")

def log(msg):
    """同時輸出到控制台和文件"""
    print(msg)
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# 清空輸出文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('')

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

log("=" * 60)
log("BGE-M3 驗證測試")
log("=" * 60)

try:
    log("\n[Step 1] 導入依賴...")
    import numpy as np
    from FlagEmbedding import BGEM3FlagModel
    log("[OK] 依賴導入成功")

    log("\n[Step 2] 導入 BGEM3Embedding...")
    from src.embeddings.bge_m3 import BGEM3Embedding
    log("[OK] BGEM3Embedding 導入成功")

    log("\n[Step 3] 實例化 BGEM3Embedding（載入模型）...")
    log("[INFO] 這可能需要 10-30 秒...")
    embedder = BGEM3Embedding()
    log("[OK] 實例化成功")

    log("\n[Step 4] 測試單文本嵌入...")
    result = embedder.embed("測試文本")
    log(f"[OK] 返回向量維度: {len(result)}")
    assert len(result) == 1024, f"Expected 1024, got {len(result)}"
    log("[OK] 維度驗證通過")

    log("\n[Step 5] 測試空文本錯誤...")
    try:
        embedder.embed("")
        log("[FAIL] 應該拋出 ValueError")
    except ValueError as e:
        if "不能嵌入空文本" in str(e):
            log("[OK] 錯誤處理正確")
        else:
            log(f"[FAIL] 錯誤訊息不正確: {e}")

    log("\n[Step 6] 測試批次嵌入...")
    results = embedder.batch_embed(["文本1", "文本2", "文本3"])
    log(f"[OK] 返回 {len(results)} 個向量")
    assert len(results) == 3
    log("[OK] 批次嵌入驗證通過")

    log("\n[Step 7] 測試模型配置...")
    log(f"   - 模型名稱: {embedder.model_name}")
    log(f"   - FP16: {embedder.use_fp16}")
    log(f"   - 設備: {embedder.device}")
    log(f"   - 最大長度: {embedder.max_length}")
    assert embedder.model_name == "BAAI/bge-m3"
    assert embedder.use_fp16 is True
    assert embedder.device == "cpu"
    assert embedder.max_length == 8192
    log("[OK] 配置驗證通過")

    log("\n" + "=" * 60)
    log("驗證結果")
    log("=" * 60)
    log("\n[SUCCESS] 所有測試通過！")
    log("\n[INFO] 下一步：提交 Green Phase")
    log("git commit -m 'feat(TDD-Green): 實現 BGE-M3 Embedder'")

except Exception as e:
    log(f"\n[ERROR] 測試失敗: {e}")
    import traceback
    log("\n詳細錯誤：")
    log(traceback.format_exc())
    sys.exit(1)
