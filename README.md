# Mem0Evomem - 全球最強中文 AI 記憶系統

**版本**: v1.0.0-dev (Week 2-3 Phase 3)
**狀態**: ✅ TDD Refactor Phase 完成，代碼品質優化完成
**基於**: [mem0](https://github.com/mem0ai/mem0) (Apache 2.0)

---

## 🎯 專案概述

Mem0Evomem 是基於 mem0 的中文優化增強版，結合了 mem0 的完整功能與 EvoMem 的中文優化技術，打造全球最強的中文 AI 記憶系統。

### 核心價值

- ✅ **中文準確度**: 目標 44% → **95%+** (+116%)
- ✅ **功能完整性**: 目標 40% → **93%+** (+133%)
- ✅ **100% 向後兼容**: 完全兼容 mem0 API
- ✅ **生態系統**: LangChain + LlamaIndex + MCP

---

## 📊 當前開發狀態 (Week 2-3)

### ✅ Phase 0: SBE (Specification by Example)
- [x] 創建 BDD 規範文件 (features/bge_m3.feature)
- [x] 19 個 Scenarios 定義完成

### ✅ Phase 1: TDD Red
- [x] 19 個單元測試（tests/unit/test_bge_m3.py）
- [x] 測試全部失敗（預期行為）

### ✅ Phase 2: TDD Green
- [x] BGEM3Embedding 類別實現 (src/embeddings/bge_m3.py)
- [x] embed() 方法：單文本嵌入 → 1024 維向量
- [x] batch_embed() 方法：批次嵌入支援
- [x] 基本錯誤處理：空文本驗證
- [x] 語法驗證通過 (Steps 1-7)
- [x] 提交 Green Phase commit (1dc6631)

### ✅ Phase 3: TDD Refactor (完成)
- [x] 類型註解完整性：100% (embed/batch_embed 返回類型)
- [x] 提取 _validate_texts() 方法降低複雜度
- [x] 魔術數字改為類常量 (DEFAULT_BATCH_SIZE, CHAR_TO_TOKEN_RATIO)
- [x] **品質指標**：
  - Radon CC: 平均 **3.33 (A級)** ✅
  - Flake8: **0 errors** ✅
  - Python Syntax: **OK** ✅
- [x] 同步優化到 mem0-evomem 倉庫
- [x] Git 提交 (002f40b4)

### 🎯 Phase 4: mem0 Integration (進行中)
- [x] 創建符合 mem0 接口的 Provider (mem0-evomem/mem0/embeddings/bge_m3.py)
- [x] 註冊 bge_m3 provider (factory.py + configs.py)
- [x] 代碼品質優化 (CC=5.0 A級)
- [ ] 集成測試與 mem0 Memory
- [ ] 性能基準測試

---

## 🏗️ 目錄結構

```
Mem0Evomem/
├── README.md                    # 專案說明
├── DEVELOPMENT_WORKFLOW.md     # 開發工作流程 (完整 TDD)
├── ERROR_DIAGNOSIS.md           # 環境兼容性診斷
├── VERIFICATION_GUIDE.md        # 驗證指南
│
├── src/                         # 💻 源代碼
│   ├── embeddings/
│   │   └── bge_m3.py           # BGE-M3 Embedder (已實現)
│   └── reranker/
│       └── bge_reranker.py     # BGE Reranker (待實現)
│
├── tests/                       # 🧪 測試
│   ├── unit/
│   │   └── test_bge_m3.py      # BGE-M3 單元測試 (19 tests)
│   ├── integration/
│   └── benchmarks/
│
├── features/                    # 📋 BDD 規範
│   └── bge_m3.feature          # BGE-M3 Scenarios (19)
│
└── syntax_test.py               # AST 語法驗證工具
```

---

## 🚀 快速開始

### 環境要求

- Python 3.9+ (推薦 3.11 或 3.12，避免 3.13)
- mem0 1.0+
- FlagEmbedding 1.3.5+

**注意**: Windows + Python 3.13 + torchvision 存在兼容性問題，詳見 [ERROR_DIAGNOSIS.md](ERROR_DIAGNOSIS.md)

### 安裝

```bash
# 克隆專案
git clone https://github.com/zycaskevin/mem0-Evomen.git
cd Mem0Evomem

# 安裝依賴
pip install -r requirements.txt
```

### 基本使用

```python
from src.embeddings.bge_m3 import BGEM3Embedding

# 創建 embedder 實例
embedder = BGEM3Embedding(
    model_name="BAAI/bge-m3",
    use_fp16=True,
    device="cpu",
    max_length=8192
)

# 單文本嵌入
vector = embedder.embed("Python 是一種強大的程式語言")
print(f"向量維度: {len(vector)}")  # 輸出: 1024

# 批次嵌入
texts = ["文本1", "文本2", "文本3"]
vectors = embedder.batch_embed(texts, batch_size=32)
print(f"批次嵌入: {len(vectors)} 個向量")  # 輸出: 3
```

### 運行測試

```bash
# 語法驗證（AST parsing，無需環境）
python syntax_test.py

# 單元測試（需要 Python 3.11 或 Linux/WSL）
pytest tests/unit/test_bge_m3.py -v

# 使用 Windows 批次文件
RUN_TEST.bat
```

---

## 📖 文檔導覽

### 開發規範文檔（必讀）⭐⭐⭐

1. **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** ⭐ **開發必讀**
   - 完整開發工作流程（SBE + TDD + 多專家協作）
   - 基於 CODEX 啟動指南 v1.0 + CLAUDE.md v3.5
   - Phase 0-6 完整流程
   - 多專家角色矩陣（小秘、小研、小品、小架、小質、小程、小憶、小數、小策）

2. **[ERROR_DIAGNOSIS.md](ERROR_DIAGNOSIS.md)** ⭐ 環境問題診斷
   - Windows + Python 3.13 + torchvision 兼容性問題
   - 4 種解決方案（Python 3.11, Linux/WSL, CPU-only, Mock）
   - 完整錯誤分析與驗證矩陣

3. **[VERIFICATION_GUIDE.md](VERIFICATION_GUIDE.md)** - 驗證流程
   - 完整驗證步驟（3000+ 字）
   - 手動驗證指南
   - 自動化測試腳本

---

## 🛠️ 開發狀態

### Week 1 ✅ 已完成
- [x] Git 初始化與遠程連接
- [x] 開發文檔創建

### Week 2 Phase 2 ✅ 已完成 (當前)
- [x] SBE .feature 文件 (19 scenarios)
- [x] TDD Red 測試 (19 tests)
- [x] **TDD Green 實現** (BGEM3Embedding 類別)
- [x] 語法驗證通過
- [x] Git commit 提交 (1dc6631)

### Week 2 Phase 3 ⏳ 下一步
- [ ] TDD Refactor - 重構優化
- [ ] 類型檢查 (mypy --strict)
- [ ] 複雜度分析 (radon cc)
- [ ] 完整文檔

### Week 3-4 ⏳ 待開始
- [ ] Python 3.11 環境設置
- [ ] 完整運行時測試
- [ ] BGE Reranker 整合
- [ ] 性能基準測試

---

## 🎯 成功指標

| 指標 | 目標 | 當前狀態 |
|------|------|---------|
| BGE-M3 實現 | 完成 | ✅ 已完成 |
| 語法驗證 | 通過 | ✅ 通過 (Steps 1-7) |
| 單元測試 | 19 tests | ✅ 已創建 |
| 運行時測試 | 通過 | ⏳ 環境限制 (Week 3) |
| 測試覆蓋率 | >90% | ⏳ 待測量 |

---

## 🤝 貢獻指南

本專案遵循 TDD (Test-Driven Development) 開發流程：

1. **Phase 0**: 創建 BDD .feature 文件
2. **Phase 1**: 寫測試（Red）
3. **Phase 2**: 最小實現（Green）
4. **Phase 3**: 重構（Refactor）

詳見 [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)

---

## 📄 授權

本專案基於 [mem0](https://github.com/mem0ai/mem0) 開發，遵循 Apache 2.0 授權。

新增代碼（BGE-M3 Embedder, BGE Reranker）採用 MIT 授權。

---

## 🙏 致謝

- **mem0ai** - 提供優秀的基礎架構 ([GitHub](https://github.com/mem0ai/mem0))
- **FlagEmbedding** - BGE-M3 和 BGE Reranker ([GitHub](https://github.com/FlagOpen/FlagEmbedding))
- **EvoMem Team** - 中文優化技術

---

## 📞 聯繫方式

- **GitHub Issues**: [Report Issues](https://github.com/zycaskevin/mem0-Evomen/issues)
- **Email**: zycaskevin@example.com

---

**專案維護者**: EvoMem Team + zycaskevin

**最後更新**: 2025-11-14

**版本**: v1.0.0-dev (Week 2 Phase 2 完成)

**Git Commit**: 1dc6631
