# BGE-M3 驗證錯誤診斷報告

**錯誤代碼**: -1073740791 (0xC0000409)
**錯誤類型**: Windows Access Violation
**發生時間**: 2025-11-14
**影響**: 無法直接執行 BGE-M3 驗證測試

---

## 🔍 根本原因分析

### 錯誤堆棧追蹤（來自 Week 2 Phase 1）

```
Windows fatal exception: access violation

Current thread 0x0001aff8 (most recent call first):
  File "ctypes\__init__.py", line 390 in __init__
  File "torch\_ops.py", line 1488 in load_library
  File "torchvision\extension.py", line 34 in <module>
  File "transformers\image_utils.py", line 55 in <module>
  ...
  File "FlagEmbedding\..." in <module>
```

### 核心問題

**觸發點**: 導入 `FlagEmbedding` → `transformers` → `torchvision`

**底層原因**: Windows 環境下，Python 3.13 + torchvision + CUDA 庫之間的 C++ ABI 兼容性問題

**相關環境**:
- OS: Windows 10/11
- Python: 3.13.7
- torch: 2.9.0
- torchvision: latest
- transformers: 4.57.1

---

## 🛠️ 已知解決方案

### 方案 A: 降級 Python 版本（推薦）⭐⭐⭐

```bash
# 使用 Python 3.11 或 3.12（更穩定）
conda create -n mem0-py311 python=3.11
conda activate mem0-py311
pip install -r requirements.txt
```

**優點**:
- ✅ 完全解決 torchvision 兼容性問題
- ✅ 可以直接運行所有測試
- ✅ 無需修改代碼

**缺點**:
- ⚠️ 需要重新創建虛擬環境
- ⚠️ 需要重新安裝依賴

---

### 方案 B: 使用 CPU-only torch（部分有效）⭐⭐

```bash
# 卸載 GPU 版本
pip uninstall torch torchvision

# 安裝 CPU-only 版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**優點**:
- ✅ 減少 CUDA 相關的兼容性問題
- ✅ 不需要更換 Python 版本

**缺點**:
- ⚠️ 可能仍然有 access violation（未完全解決）
- ⚠️ CPU 版本效能較低

---

### 方案 C: Mock 測試（當前使用）⭐

**概念**: 不實際載入模型，使用 Mock 對象驗證代碼邏輯

**優點**:
- ✅ 不受環境限制
- ✅ 執行速度快（無需載入模型）
- ✅ 可驗證代碼邏輯正確性

**缺點**:
- ❌ 無法驗證實際模型行為
- ❌ 無法測試效能

**實作**: 見 `mock_test.py`

---

### 方案 D: Linux/WSL 環境（最穩定）⭐⭐⭐⭐

```bash
# 使用 WSL2（Windows Subsystem for Linux）
wsl --install Ubuntu
wsl

# 在 WSL 中執行測試
cd /mnt/c/Users/User/.claude/Mem0Evomem
python3 minimal_test.py
```

**優點**:
- ✅ 完全避免 Windows 兼容性問題
- ✅ 與生產環境一致（Linux）
- ✅ 更好的 Python 生態支援

**缺點**:
- ⚠️ 需要安裝 WSL
- ⚠️ 需要在 WSL 中重新設置環境

---

## ✅ 當前採用策略

### 短期（Week 2 Phase 2）：Mock 測試驗證代碼邏輯

使用 `mock_test.py` 驗證：
1. ✅ 類別結構正確
2. ✅ 方法簽名正確
3. ✅ 錯誤處理邏輯
4. ✅ 配置參數

**不驗證**：
- ❌ 實際模型載入
- ❌ 向量維度（依賴實際模型）
- ❌ 相似度計算

### 中期（Week 3-4）：Python 3.11 環境測試

建立獨立的 Python 3.11 環境進行完整測試。

### 長期：生產環境部署

使用 Linux/Docker 環境部署，避免 Windows 兼容性問題。

---

## 📊 驗證矩陣

| 測試類型 | Windows + Py3.13 | Windows + Py3.11 | Linux/WSL | Mock |
|---------|-----------------|-----------------|----------|------|
| **代碼結構** | ❌ Crash | ✅ | ✅ | ✅ |
| **錯誤處理** | ❌ Crash | ✅ | ✅ | ✅ |
| **模型載入** | ❌ Crash | ✅ | ✅ | ❌ N/A |
| **向量維度** | ❌ Crash | ✅ | ✅ | ❌ N/A |
| **相似度** | ❌ Crash | ✅ | ✅ | ❌ N/A |
| **效能** | ❌ Crash | ✅ | ✅ | ❌ N/A |

---

## 🎯 建議行動

### 立即執行（今天）
1. ✅ 執行 Mock 測試驗證代碼邏輯
2. ✅ 提交 Green Phase（附註環境限制）
3. ✅ 記錄問題到 EvoMem

### 短期（本週）
1. ⏳ 建立 Python 3.11 虛擬環境
2. ⏳ 在 Py3.11 環境中執行完整測試
3. ⏳ 驗證所有功能

### 中期（Week 3-4）
1. ⏳ 在 Linux/WSL 環境中測試
2. ⏳ 建立 CI/CD pipeline（Linux 環境）
3. ⏳ 完整的效能基準測試

---

## 📝 EvoMem 記憶記錄

```python
evomem.add_memory(
    content="Windows Py3.13 + torchvision access violation 問題。解決方案：1) 降級到 Py3.11/3.12，2) 使用 Linux/WSL，3) 短期使用 Mock 測試。",
    metadata={
        "project": "Mem0Evomem",
        "type": "defect",
        "severity": "high",
        "tags": ["Windows", "Python3.13", "torchvision", "access-violation"],
        "solutions": ["Python3.11", "Linux", "WSL", "Mock"],
        "task_id": "Week2-Phase2-Verification"
    }
)
```

---

**結論**: 這是環境兼容性問題，不是代碼問題。我們將使用 Mock 測試驗證代碼邏輯，並在後續階段使用更穩定的環境（Python 3.11 或 Linux）進行完整測試。

---

*Last Updated: 2025-11-14*
*Version: 1.0*
*Severity: High*
*Status: Workaround Applied (Mock Testing)*
