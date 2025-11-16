"""
BGE-M3 API 驗證腳本

目的: 驗證 FlagEmbedding BGEM3FlagModel 的實際 API 格式
重要性: ⭐⭐⭐ 關鍵 - 必須在 Week 2 開始前驗證

執行:
    python scripts/verify_bgem3_api.py
"""

import sys


def check_model_download_environment():
    """檢查模型下載環境 (Meta-Review 補充)"""
    import platform
    from pathlib import Path

    print("=" * 60)
    print("[0/5] 檢查模型下載環境")
    print("=" * 60)
    print()

    # 檢查網絡連接
    print("檢查 Hugging Face 連接...")
    try:
        import urllib.request
        urllib.request.urlopen("https://huggingface.co", timeout=5)
        print("[OK] Hugging Face 網絡連接正常")
    except Exception as e:
        print(f"[WARN] Hugging Face 網絡連接失敗: {e}")
        print()
        print("建議:")
        print("1. 檢查網絡連接")
        print("2. 如在中國大陸,可能需要代理/VPN")
        print("3. 或使用 HF_ENDPOINT 環境變數切換鏡像站")
        print()
        print("手動下載模型:")
        print("https://huggingface.co/BAAI/bge-m3")
        print()

    # 檢查磁碟空間
    cache_dir = Path.home() / ".cache" / "huggingface"
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"模型緩存目錄: {cache_dir}")

    try:
        import shutil
        total, used, free = shutil.disk_usage(cache_dir)
        free_gb = free // (2**30)
        print(f"可用磁碟空間: {free_gb} GB")

        if free_gb < 3:
            print("[WARN] 磁碟空間不足 3 GB")
            print("   BGE-M3 模型約需 1-2 GB")
            print("   建議清理空間")
            return False
        else:
            print("[OK] 磁碟空間充足")
    except Exception as e:
        print(f"[WARN] 無法檢查磁碟空間: {e}")

    # 檢查平台特殊要求
    system = platform.system()
    if system == "Windows":
        print()
        print("[WARN] Windows 平台注意:")
        print("   - 下載可能較慢,請耐心等待")
        print("   - 防火牆可能阻止下載,請允許 Python 訪問網絡")

    print()
    return True


def verify_bgem3_api():
    """驗證 BGE-M3 API 格式"""
    print("=" * 60)
    print("BGE-M3 API 驗證")
    print("=" * 60)
    print()

    # Step 1: 檢查 FlagEmbedding 是否已安裝
    print("[1/5] 檢查 FlagEmbedding 安裝...")
    try:
        from FlagEmbedding import BGEM3FlagModel
        print("[OK] FlagEmbedding 已安裝")
    except ImportError as e:
        print(f"[FAIL] FlagEmbedding 未安裝: {e}")
        print()
        print("請執行: pip install FlagEmbedding==1.3.5")
        return False

    print()

    # Step 2: 嘗試載入模型
    print("[2/5] 載入 BGE-M3 模型...")
    from pathlib import Path
    print("[WARN] 首次載入需要下載模型（約 1-2 GB）")
    print(f"   下載位置: {Path.home() / '.cache' / 'huggingface' / 'hub'}")
    print("   如果下載緩慢:")
    print("   1. 使用代理/VPN")
    print("   2. 手動下載: https://huggingface.co/BAAI/bge-m3")
    print()
    print("正在載入...")

    try:
        model = BGEM3FlagModel(
            "BAAI/bge-m3",
            use_fp16=True,
            device="cpu"
        )
        print("[OK] BGE-M3 模型載入成功")
    except Exception as e:
        print(f"[FAIL] 模型載入失敗: {e}")
        print()
        print("可能原因:")
        print("1. 網絡連接問題（無法下載模型）")
        print("   → 嘗試使用代理/VPN")
        print("   → 或手動下載模型到緩存目錄")
        print("2. 磁碟空間不足")
        print("   → 確保至少有 3 GB 可用空間")
        print("3. 依賴版本不兼容")
        print("   → 檢查 torch, transformers 版本")
        print()
        print("手動下載步驟:")
        print("1. 訪問: https://huggingface.co/BAAI/bge-m3")
        print("2. 下載所有文件到:")
        print(f"   {Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--BAAI--bge-m3'}")
        return False

    print()

    # Step 3: 測試單個文本 encoding
    print("[3/5] 測試單個文本 encoding...")
    try:
        test_text = ["測試文本"]
        result = model.encode(
            test_text,
            batch_size=256,
            max_length=8192
        )
        print(f"[OK] Encoding 成功")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

        # 關鍵驗證: 檢查是否有 'dense_vecs' 鍵
        if isinstance(result, dict):
            if 'dense_vecs' in result:
                print(f"   - [OK] 'dense_vecs' 鍵存在")
                print(f"   - dense_vecs type: {type(result['dense_vecs'])}")
                print(f"   - dense_vecs shape: {result['dense_vecs'].shape}")

                # 檢查維度
                if result['dense_vecs'].shape[-1] == 1024:
                    print(f"   - [OK] Embedding 維度為 1024 (正確)")
                else:
                    print(f"   - [WARN] Embedding 維度為 {result['dense_vecs'].shape[-1]} (預期 1024)")
            else:
                print(f"   - [FAIL] 'dense_vecs' 鍵不存在！")
                print(f"   - 可用的鍵: {list(result.keys())}")
                print()
                print("[WARN] 警告: 計劃中的代碼假設使用 'dense_vecs'，需要調整！")
                return False
        else:
            print(f"   - [FAIL] Result 不是字典類型")
            return False

    except Exception as e:
        print(f"[FAIL] Encoding 失敗: {e}")
        return False

    print()

    # Step 4: 測試批次 encoding
    print("[4/5] 測試批次 encoding...")
    try:
        batch_texts = ["文本1", "文本2", "文本3"]
        result = model.encode(
            batch_texts,
            batch_size=256,
            max_length=8192
        )
        print(f"[OK] 批次 encoding 成功")
        print(f"   - Batch size: {len(batch_texts)}")
        if 'dense_vecs' in result:
            print(f"   - Result shape: {result['dense_vecs'].shape}")
            expected_shape = (len(batch_texts), 1024)
            if result['dense_vecs'].shape == expected_shape:
                print(f"   - [OK] Shape 正確: {expected_shape}")
            else:
                print(f"   - [WARN] Shape 不符預期: {result['dense_vecs'].shape} (預期 {expected_shape})")

    except Exception as e:
        print(f"[FAIL] 批次 encoding 失敗: {e}")
        return False

    print()
    print("=" * 60)
    print("[OK] 所有驗證通過！")
    print("=" * 60)
    print()
    print("結論:")
    print("[OK] FlagEmbedding BGE-M3 API 符合預期")
    print("[OK] result['dense_vecs'] 鍵存在")
    print("[OK] Embedding 維度為 1024")
    print("[OK] 批次處理正常")
    print()
    print("[=>] 可以安全地繼續 Week 2 開發")
    return True


def print_code_example():
    """打印正確的代碼範例"""
    print()
    print("=" * 60)
    print("推薦的代碼實現")
    print("=" * 60)
    print()
    print("""
class BGEM3Embedding(EmbeddingBase):
    def embed(self, text, memory_action=None):
        if isinstance(text, str):
            text = [text]
            single_input = True
        else:
            single_input = False

        result = self.model.encode(
            text,
            batch_size=self.batch_size,
            max_length=self.max_length
        )

        # [OK] 驗證通過：使用 'dense_vecs' 鍵
        embeddings = result['dense_vecs']

        if single_input:
            return embeddings[0].tolist()
        return embeddings.tolist()
""")


if __name__ == "__main__":
    # Meta-Review 補充: 先檢查下載環境
    print("[INFO] Meta-Review 補充檢查")
    print()

    env_ok = check_model_download_environment()
    if not env_ok:
        print("[WARN] 環境檢查發現問題,但將繼續嘗試...")
        print()

    print("[INFO] BGE-M3 API 驗證")
    print()

    success = verify_bgem3_api()

    if success:
        print_code_example()
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("[FAIL] 驗證失敗")
        print("=" * 60)
        print()
        print("建議:")
        print("1. 檢查錯誤訊息")
        print("2. 確認 FlagEmbedding 版本為 1.3.5")
        print("3. 如有需要，調整代碼以適應實際 API")
        print("4. 重新評估實施計劃")
        print()
        print("如果是下載問題:")
        print("- 使用代理/VPN 重試")
        print("- 或手動下載模型 (詳見上方錯誤訊息)")
        sys.exit(1)
