"""
mem0 Reranker 接口驗證腳本

目的: 驗證 mem0 的 Reranker 接口定義和調用方式
重要性: ⭐⭐⭐ 關鍵 - 必須在 Week 4 開始前驗證

執行:
    cd mem0-evomem  # 必須在 fork 的 mem0 目錄中執行
    python ../scripts/verify_reranker_interface.py
"""

import sys
import inspect
from pathlib import Path


def verify_reranker_interface():
    """驗證 mem0 Reranker 接口"""
    print("=" * 60)
    print("mem0 Reranker 接口驗證")
    print("=" * 60)
    print()

    # Step 1: 檢查是否在 mem0 目錄中
    print("[1/5] 檢查 mem0 環境...")
    if not Path("mem0").exists():
        print("[FAIL] 未找到 mem0 目錄")
        print()
        print("請在 fork 的 mem0 目錄中執行此腳本:")
        print("cd mem0-evomem")
        print("python ../scripts/verify_reranker_interface.py")
        return False
    print("[OK] 在 mem0 目錄中")
    print()

    # Step 2: 嘗試 import mem0
    print("[2/5] 導入 mem0...")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from mem0.memory.main import Memory
        print("[OK] mem0 導入成功")
    except ImportError as e:
        print(f"[FAIL] mem0 導入失敗: {e}")
        print()
        print("請確認:")
        print("1. 已安裝 mem0: pip install mem0ai")
        print("2. 在正確的目錄中")
        return False

    print()

    # Step 3: 檢查 Memory 是否有 reranker 屬性
    print("[3/5] 檢查 Memory.reranker 屬性...")
    try:
        # 創建一個測試 Memory 實例
        memory = Memory()

        if hasattr(memory, 'reranker'):
            print("[OK] Memory 有 reranker 屬性")
            print(f"   - Type: {type(memory.reranker)}")
            print(f"   - Value: {memory.reranker}")

            if memory.reranker is not None:
                print(f"   - [OK] reranker 已初始化")
                print(f"   - Class: {memory.reranker.__class__.__name__}")
            else:
                print(f"   - [WARN] reranker 為 None（未配置）")
        else:
            print("[FAIL] Memory 沒有 reranker 屬性")
            print()
            print("[WARN] 這可能表示計劃中的假設有誤")
            return False

    except Exception as e:
        print(f"[FAIL] 檢查失敗: {e}")
        return False

    print()

    # Step 4: 檢查 search 方法是否有 rerank 參數
    print("[4/5] 檢查 Memory.search() 方法...")
    try:
        sig = inspect.signature(memory.search)
        params = sig.parameters

        print(f"[OK] search 方法存在")
        print(f"   - 參數: {list(params.keys())}")

        if 'rerank' in params:
            print(f"   - [OK] 有 'rerank' 參數")
            print(f"   - 默認值: {params['rerank'].default}")
        else:
            print(f"   - [FAIL] 沒有 'rerank' 參數")
            print()
            print("[WARN] 警告: 計劃假設 search() 有 rerank 參數，但實際沒有！")
            return False

    except Exception as e:
        print(f"[FAIL] 檢查失敗: {e}")
        return False

    print()

    # Step 5: 查找 reranker 源碼
    print("[5/5] 查找 reranker 源碼...")
    try:
        # 搜尋 reranker 相關文件
        import os

        reranker_files = []
        for root, dirs, files in os.walk("mem0"):
            for file in files:
                if 'rerank' in file.lower() and file.endswith('.py'):
                    reranker_files.append(os.path.join(root, file))

        if reranker_files:
            print(f"[OK] 找到 {len(reranker_files)} 個 reranker 相關文件:")
            for f in reranker_files:
                print(f"   - {f}")
        else:
            print("[WARN] 未找到 reranker 相關文件")

    except Exception as e:
        print(f"[FAIL] 搜尋失敗: {e}")

    print()

    # Step 6: 嘗試讀取源碼中的 reranker 調用
    print("[6/6] 檢查 reranker 調用邏輯...")
    try:
        memory_main_path = Path("mem0/memory/main.py")
        if memory_main_path.exists():
            with open(memory_main_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找 reranker 調用
            if 'reranker.rerank' in content:
                print("[OK] 在 main.py 中找到 reranker.rerank 調用")

                # 提取相關代碼
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'reranker.rerank' in line:
                        # 打印上下文（前後 3 行）
                        print()
                        print("   相關代碼片段:")
                        for j in range(max(0, i-3), min(len(lines), i+4)):
                            prefix = "   >>>" if j == i else "      "
                            print(f"{prefix} {lines[j]}")
                        break
            else:
                print("[WARN] 未在 main.py 中找到 reranker.rerank 調用")

        else:
            print("[FAIL] 未找到 mem0/memory/main.py")

    except Exception as e:
        print(f"[WARN] 讀取源碼失敗: {e}")

    print()
    print("=" * 60)
    print("驗證完成")
    print("=" * 60)
    return True


def print_recommendations():
    """打印建議"""
    print()
    print("=" * 60)
    print("建議的 BGEReranker 實現")
    print("=" * 60)
    print()
    print("""
# 基於驗證結果的推薦實現

from typing import List, Dict, Any
from FlagEmbedding import FlagReranker

class BGEReranker:
    \"\"\"BGE Reranker for mem0\"\"\"

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.reranker = FlagReranker(
            model_name,
            use_fp16=True,
            device="cpu"
        )

    def rerank(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        \"\"\"
        Rerank memories based on query relevance.

        Args:
            query: User query string
            memories: List of memory dicts (mem0 format)
            limit: Maximum number of results

        Returns:
            Reranked list of memories
        \"\"\"
        if not memories:
            return []

        # 提取文本
        texts = [m.get('memory', '') for m in memories]

        # 創建 query-text pairs
        pairs = [[query, text] for text in texts]

        # 計算相關性分數
        scores = self.reranker.compute_score(
            pairs,
            batch_size=256,
            normalize=True
        )

        # 排序
        ranked = sorted(
            zip(memories, scores),
            key=lambda x: x[1],
            reverse=True
        )

        # 返回前 limit 個結果
        return [m for m, s in ranked[:limit]]
""")
    print()
    print("[WARN] 注意:")
    print("1. 確認 memories 的實際格式（通過查看 mem0 源碼）")
    print("2. 驗證是否需要保留原始的 'id' 和 'metadata'")
    print("3. 測試與 mem0 的實際整合")


if __name__ == "__main__":
    success = verify_reranker_interface()

    if success:
        print_recommendations()
        print()
        print("[=>] 下一步:")
        print("1. 閱讀找到的 reranker 源碼文件")
        print("2. 確認 rerank() 方法的精確簽名")
        print("3. 確認 memories 參數的格式")
        print("4. 實現 BGEReranker 類別")
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("[FAIL] 驗證失敗")
        print("=" * 60)
        print()
        print("建議:")
        print("1. 確認在正確的目錄中（mem0-evomem/）")
        print("2. 確認 mem0 已正確安裝")
        print("3. 檢查 mem0 版本是否為 1.0+")
        print("4. 查閱 mem0 官方文檔")
        sys.exit(1)
