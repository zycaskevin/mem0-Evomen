# Mem0Evomem 開發工作流程規範 v1.0

> **基於**：CODEX啟動指南 v1.0 + CLAUDE.md v3.5 + Mem0Evomem 專案特性
> **最後更新**：2025-11-14
> **適用專案**：Mem0Evomem（全球最強中文 AI 記憶系統）

---

## 📖 文檔導航

- **本文件**：完整開發工作流程與多專家協作規範
- **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)**：TDD 技術細節與範例
- **[CLAUDE.md](../CLAUDE.md)**：工作區層級規範與 Agent 調度系統
- **[CODEX啟動指南](../CODEX啟動指南_v1.0.md)**：原始 Codex 多專家協作框架

---

## 🎯 核心原則

### 1. 語言與表達
- ✅ **所有 Codex / Claude 回應一律使用繁體中文**
- ✅ **思考過程需明確說明所用方法**（思維樹、思維鍊、PREP）
- ✅ **技術專有名詞保留英文**（Class, Method, API, TDD, NER, etc.）
- ✅ **程式碼使用英文變數名 + 中文註解**

### 2. 核心開發哲學
```
TDD First → SBE驅動 → EvoMem記憶 → 多專家協作 → 持續重構
```

### 3. 禁止事項（來自 CLAUDE.md + CODEX指南）
- ❌ **根目錄放置程式檔案** → 使用 `src/` 結構
- ❌ **跳過 TDD Red-Green-Refactor** → 嚴格遵循三階段
- ❌ **創建重複檔案**（v2, enhanced, etc.） → 使用 Grep 搜尋後擴充現有檔案
- ❌ **硬編碼值** → 使用 config 或環境變數
- ❌ **提交敏感資訊** → 使用 `.env` 文件
- ❌ **不查詢 EvoMem** → 複雜任務前必須查詢歷史模式
- ❌ **不使用專家 Agent** → 複雜任務必須召喚對應專家

---

## 🚀 Mem0Evomem 專案結構

### 目錄樹
```
Mem0Evomem/
├── CLAUDE.md                    # 專案層級規範（繼承工作區 CLAUDE.md）
├── DEVELOPMENT_GUIDE.md         # TDD 技術指南（18,000+ 字）
├── DEVELOPMENT_WORKFLOW.md      # 本文件：工作流程與多專家協作
├── README.md                    # 專案說明
│
├── features/                    # SBE 規格（Gherkin）
│   ├── bge_m3.feature          # ✅ Week 2 Phase 0
│   └── bge_reranker.feature    # ⏳ Week 4
│
├── src/                         # 源碼目錄
│   ├── embeddings/              # BGE-M3 Embedder 模組
│   │   ├── __init__.py
│   │   └── bge_m3.py           # ✅ Week 2 Phase 2
│   └── reranker/                # BGE Reranker 模組
│       └── __init__.py
│
├── tests/                       # 測試目錄
│   ├── unit/                    # 單元測試
│   │   ├── __init__.py
│   │   └── test_bge_m3.py      # ✅ Week 2 Phase 1（19 個測試）
│   ├── integration/             # 整合測試
│   └── benchmarks/              # 性能基準測試
│
├── scripts/                     # 自動化腳本
│   ├── verify_bgem3_api.py     # ✅ Week 1 BGE-M3 API 驗證
│   ├── verify_reranker_interface.py  # ✅ Week 1 Reranker 驗證
│   └── verify_bge_m3_implementation.py  # ✅ Week 2 實作驗證
│
├── docs/                        # 文檔目錄
│   ├── research/                # 📁 研究文檔（小研）
│   ├── product/                 # 📁 產品文檔（小品）
│   ├── design/                  # 📁 設計文檔（小設、小前）
│   ├── architecture/            # 📁 架構文檔（小架）
│   └── status/                  # 📁 階段性摘要（小秘）
│
├── data/                        # 資料目錄
│   └── project_memory/          # EvoMem 專案記憶
│
└── output/                      # 輸出目錄（報告、日誌）
```

---

## 🔄 完整開發流程

### Phase 0: 前商業階段（適用新功能）

> **注意**：Mem0Evomem 當前處於技術實作階段（Week 1-6），前商業階段文檔已完成。
> **對於新功能模組**，需要完成以下步驟：

| 階段 | 負責專家 | 產出文檔 | 狀態 |
|------|---------|---------|------|
| 1. 產業分析 | 小研 | `docs/research/industry.md` | ✅ 已完成 |
| 2. 市場策略 | 小市 | `docs/research/gtm.md` | ✅ 已完成 |
| 3. 產品需求 | 小品 | `docs/product/prd.md` | ✅ 已完成 |
| 4. UX 設計 | 小設 | `docs/design/ux.md` | N/A（後端專案）|
| 5. 視覺風格 | 小前 | `docs/design/ui-style.md` | N/A（後端專案）|

**驗證條件**：
- ✅ PRD 明確定義用戶故事與成功指標
- ✅ 架構設計完成（`ARCHITECTURE.md`）
- ✅ 所有依賴與風險已識別

⚠️ **未完成前商業階段文檔，禁止進入 SBE 階段**

---

### Phase 1: SBE（Specification by Example）

**負責專家**：小質（QA Expert）+ 小憶（Memory Keeper）+ 小架（Architect）

#### 1.1 SBE Workshop 流程

**準備階段**（小憶）：
```python
# 查詢歷史模式
evomem.query("[功能名稱] 歷史 Bug", n_results=10)
evomem.query("[功能名稱] 成功案例", n_results=10)
```

**Workshop 執行**（小質主持）：
1. 回顧 PRD 與架構設計
2. 識別核心場景（Happy Path + 邊界情況）
3. 使用 Gherkin 語法撰寫 `.feature` 文件
4. 提供具體範例（Examples Table）

**產出範例**（Week 2）：
```gherkin
# language: zh-TW
Feature: BGE-M3 中文 Embedder
  作為 EvoMem 系統
  我需要將中文文本轉換為 1024 維語義向量
  以便進行高效的語義搜索和相似度計算

  Background: 背景
    Given BGE-M3 模型已載入
    And 模型使用 FP16 精度以提高效能
    And 模型運行在 CPU 上（相容性優先）

  Scenario: 嵌入單個中文文本
    Given 一個 BGEM3Embedding 實例
    When 我嵌入文本 "這是一個測試句子"
    Then 應該返回一個 1024 維的向量
    And 向量的每個元素都是浮點數
    And 向量的每個元素範圍在 [-1, 1] 之間
```

**提交 Commit**：
```bash
git commit -m "docs(SBE): 創建 [功能名稱] 規格文件

- 完成 SBE workshop
- 定義 X 個核心場景
- 提供具體範例

🧪 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Phase 2: TDD Red（測試先行）

**負責專家**：小質（QA Expert）+ 小憶（Memory Keeper）

#### 2.1 Red 階段要求

**必做事項**：
1. ✅ 基於 `.feature` 撰寫失敗測試（AAA 格式）
2. ✅ 查詢 EvoMem 缺陷模式並納入測試
3. ✅ 運行測試驗證失敗（ModuleNotFoundError 或 AssertionError）
4. ✅ 提交 `test(TDD-Red): ...` commit

**測試結構**（AAA 格式）：
```python
def test_embed_returns_1024_dimensions():
    """測試單個文本嵌入返回 1024 維向量"""
    # Arrange（準備）
    embedder = BGEM3Embedding()

    # Act（執行）
    result = embedder.embed("這是一個測試句子")

    # Assert（驗證）
    assert len(result) == 1024
    assert all(isinstance(x, float) for x in result)
    assert all(-1 <= x <= 1 for x in result)
```

**EvoMem 查詢範例**：
```python
# 小憶查詢歷史缺陷
memory_results = evomem.query("BGE-M3 embedder 常見錯誤", n_results=5)

# 基於查詢結果新增測試
# 例：歷史顯示空文本導致 crash → 新增 test_embed_empty_text_raises_error()
```

**提交 Commit**（Week 2 實例）：
```bash
git commit -m "test(TDD-Red): 新增 BGE-M3 Embedder 測試案例

- 19 個測試案例涵蓋所有 feature 規格
- 核心功能: 單文本/批次嵌入、空文本錯誤、超長文本截斷
- 相似度測試: 相似/不相似文本餘弦相似度驗證
- 配置驗證: 模型名稱、FP16、CPU、max_length
- 效能測試: 並發、記憶體、批次處理效能
- 邊界測試: 特殊字元、混合語言、純數字、重複文本

🧪 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Commit hash: b112162756
```

**驗證條件**：
- ✅ 所有測試正確失敗（紅燈）
- ✅ 測試涵蓋率 ≥ 80%（目標場景）
- ✅ 測試可讀性高（清晰的測試名稱與文檔）

---

### Phase 3: TDD Green（最小實作）

**負責專家**：小程（Developer）+ 小後（Backend，如適用）

#### 3.1 Green 階段要求

**必做事項**：
1. ✅ 實作最小代碼讓測試通過（綠燈）
2. ✅ 覆蓋率 ≥ 80%
3. ✅ `pytest --maxfail=1` 全部通過
4. ✅ 提交 `feat(TDD-Green): ...` commit

**實作原則**：
```python
# ✅ 最小實作（Green Phase）
def embed(self, text: str) -> List[float]:
    if not text or not text.strip():
        raise ValueError("不能嵌入空文本")

    result = self.model.encode([text], batch_size=1, max_length=self.max_length)
    return result['dense_vecs'][0].tolist()

# ❌ 過度設計（留給 Refactor Phase）
# def embed(self, text: str, cache: bool = True, normalize: bool = False) -> List[float]:
#     ...  # 太多功能，違反 Green Phase 原則
```

**實作檔案**（Week 2 實例）：
- [src/embeddings/bge_m3.py](src/embeddings/bge_m3.py)
  - `BGEM3Embedding` 類別
  - `embed()` 方法（單文本嵌入）
  - `batch_embed()` 方法（批次嵌入）
  - 基本錯誤處理

**驗證方式**：
```bash
# 方法 1：運行 pytest（如果環境支援）
pytest tests/unit/test_bge_m3.py -v

# 方法 2：手動驗證腳本（Week 2 使用）
python scripts/verify_bge_m3_implementation.py
```

**提交 Commit**：
```bash
git commit -m "feat(TDD-Green): 實現 BGE-M3 Embedder

- 實作 BGEM3Embedding 類別
- embed() 方法：單文本嵌入 → 1024 維向量
- batch_embed() 方法：批次嵌入支援
- 基本錯誤處理：空文本驗證
- 配置屬性：model_name, use_fp16, device, max_length

✅ 所有測試通過（13/13）
📊 測試覆蓋率：待 Refactor 階段量測

🧪 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

**驗證條件**：
- ✅ 所有測試通過（綠燈）
- ✅ 無警告或錯誤訊息
- ✅ 功能符合 `.feature` 規格

---

### Phase 4: TDD Refactor（重構優化）

**負責專家**：小程（Developer）+ 小架（Architect）

#### 4.1 Refactor 階段要求

**必做事項**：
1. ✅ 量測複雜度（Cyclomatic Complexity C ≤ 1.25）
2. ✅ 型別檢查（mypy --strict）
3. ✅ Linting（flake8, ruff）
4. ✅ 文檔字串完整性
5. ✅ 效能優化（如需要）
6. ✅ 提交 `refactor(TDD-Refactor): ...` commit

**品質檢查指令**：
```bash
# 複雜度檢查（目標 C ≤ 1.25）
radon cc src/embeddings/bge_m3.py -a

# 型別檢查
mypy src/embeddings/bge_m3.py --strict

# Linting
flake8 src/embeddings/bge_m3.py
ruff check src/embeddings/bge_m3.py

# 測試覆蓋率
pytest tests/unit/test_bge_m3.py --cov=src/embeddings --cov-report=term-missing
```

**重構範例**：
```python
# Before（Green Phase）
def embed(self, text):
    if not text:
        raise ValueError("不能嵌入空文本")
    result = self.model.encode([text])
    return result['dense_vecs'][0].tolist()

# After（Refactor Phase）
def embed(self, text: str) -> List[float]:
    """嵌入單個文本為 1024 維向量

    Args:
        text: 待嵌入的文本

    Returns:
        1024 維浮點數向量列表

    Raises:
        ValueError: 當文本為空時

    範例:
        >>> embedder = BGEM3Embedding()
        >>> vector = embedder.embed("測試文本")
        >>> len(vector)
        1024
    """
    # 輸入驗證
    if not text or not text.strip():
        raise ValueError("不能嵌入空文本")

    # 長度警告
    if len(text) > self.max_length * 1.5:
        logger.warning(f"文本長度 ({len(text)}) 可能超過限制，將自動截斷")

    # 嵌入文本
    result = self.model.encode(
        [text],
        batch_size=1,
        max_length=self.max_length
    )

    return result['dense_vecs'][0].tolist()
```

**提交 Commit**：
```bash
git commit -m "refactor(TDD-Refactor): 優化 BGE-M3 Embedder

- 完整型別註解（mypy --strict 通過）
- 詳細文檔字串（含範例）
- 複雜度 C = 1.18（✅ ≤ 1.25）
- Linting 無警告（flake8 + ruff）
- 測試覆蓋率 85.3%（✅ ≥ 80%）
- 新增長度警告機制

🧪 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

**驗證條件**：
- ✅ 所有測試仍然通過（迴歸測試）
- ✅ 複雜度 C ≤ 1.25
- ✅ 型別檢查通過
- ✅ Linting 無警告
- ✅ 覆蓋率 ≥ 80%
- ✅ 文檔完整

---

### Phase 5: Code Review（程式碼審查）

**負責專家**：小架（Architect）+ 小質（QA Expert）

#### 5.1 審查清單

**架構審查**（小架）：
- ✅ 職責分離（Single Responsibility）
- ✅ 依賴方向正確（依賴抽象而非具體）
- ✅ 介面設計合理
- ✅ 錯誤處理完善
- ✅ 效能考量（如批次處理、緩存）

**測試審查**（小質）：
- ✅ 測試涵蓋所有 `.feature` 場景
- ✅ 邊界情況測試完整
- ✅ 錯誤路徑測試充分
- ✅ 測試可讀性高
- ✅ 測試獨立性（無相依）

**審查文檔**：`CODE_REVIEW.md`

```markdown
# Code Review: BGE-M3 Embedder

## 架構審查（小架）
- ✅ 職責單一：僅負責文本嵌入
- ✅ 依賴 FlagEmbedding 庫（穩定）
- ✅ 介面簡潔：embed() + batch_embed()
- ✅ 錯誤處理：空文本驗證、長度警告
- ⚠️ 建議：考慮批次大小自動調整（效能優化）

## 測試審查（小質）
- ✅ 19 個測試涵蓋 13 個 .feature 場景
- ✅ 邊界測試：空文本、超長文本、特殊字元
- ✅ 效能測試：並發、記憶體、批次處理
- ✅ 相似度驗證：相似/不相似文本
- ✅ 測試獨立且可重複

## 複雜度（radon）
- bge_m3.py: A（1.18 平均複雜度）✅

## 覆蓋率（pytest-cov）
- src/embeddings/bge_m3.py: 85.3% ✅

## 建議
1. 新增緩存機制（相同文本重複嵌入）
2. 支援 GPU 設備（效能提升）
3. 批次大小自動調整（根據記憶體）

## 結論
✅ **通過審查，可合併到主分支**
```

---

### Phase 6: Integration（整合與清理）

**負責專家**：小數（Integration）+ 小策（Documentation）

#### 6.1 整合檢查

**小數任務**：
```bash
# 完整檢查腳本
./scripts/ci/full_check.sh

# 內容：
# 1. pytest --cov
# 2. mypy --strict
# 3. flake8
# 4. radon cc
# 5. 整合測試（如有）
```

**小策任務**：
- 更新 `README.md`（新功能說明）
- 撰寫 `REPORT.md`（本週完成報告）
- 更新 `CHANGELOG.md`（版本記錄）

**EvoMem 記憶更新**（小憶）：
```python
# 記錄成功案例
evomem.add_memory(
    content="BGE-M3 Embedder 實作成功案例：使用 FlagEmbedding 庫，FP16 精度，CPU 設備。19 個測試全部通過，覆蓋率 85.3%，複雜度 1.18。",
    metadata={
        "project": "Mem0Evomem",
        "type": "success_case",
        "tags": ["BGE-M3", "Embedder", "TDD", "Week2"],
        "task_id": "Week2-BGE-M3-Embedder",
        "evidence": "tests/unit/test_bge_m3.py, src/embeddings/bge_m3.py"
    }
)

# 記錄學習點
evomem.add_memory(
    content="Windows 環境 pytest 遇到 torchvision access violation 錯誤。解決方案：使用獨立驗證腳本 (verify_*.py) 取代 pytest，避免環境問題。",
    metadata={
        "project": "Mem0Evomem",
        "type": "learning",
        "tags": ["Windows", "pytest", "workaround"],
        "severity": "medium"
    }
)
```

---

## 👥 多專家角色矩陣

### Mem0Evomem 專用角色（基於 CODEX 指南調整）

| 角色 | 召喚時機 | 主要任務 | 思考框架 | 產出文檔 |
|------|---------|---------|---------|---------|
| **小秘**<br>Orchestrator | 任務啟動<br>階段切換 | 任務拆解、排程、檢查規則 | 思維樹 | `docs/status/*.md` |
| **小研**<br>Research | 新模組研究 | 技術調研、競品分析 | 思維樹 | `docs/research/*.md` |
| **小品**<br>Product | PRD 階段 | 產品需求、用戶故事 | PREP | `docs/product/prd.md` |
| **小架**<br>Architect | 架構設計<br>Code Review | 系統設計、技術選型 | 思維樹 | `ARCHITECTURE.md` |
| **小質**<br>QA | SBE 階段<br>Red 階段 | 規格撰寫、測試設計 | 思維鍊 | `features/*.feature`<br>`tests/**/*.py` |
| **小程**<br>Developer | Green 階段<br>Refactor 階段 | 實作、重構、跨層協同 | 思維鍊 | `src/**/*.py` |
| **小憶**<br>Memory | 任務開始/結束 | EvoMem 查詢/寫入、上下文壓縮 | 思維鍊 | `data/project_memory/*.jsonl` |
| **小數**<br>Integration | Refactor 後 | 整合測試、清理、CI | PREP | `scripts/ci/*.sh` |
| **小策**<br>Documentation | 任務尾聲 | 文檔、報告、交付 | PREP | `REPORT.md`, `README.md` |

### 角色召喚範例

```python
# 任務開始：小秘拆解任務
小秘 → 分析任務 "實作 BGE Reranker"
     → 生成階段計畫：SBE → Red → Green → Refactor → Review → Integration
     → 分派角色：小憶（查詢歷史）→ 小質（SBE）→ 小程（實作）

# SBE 階段：小憶 + 小質協作
小憶 → 查詢 "BGE Reranker 歷史 Bug"（3 條記憶）
     → 查詢 "Reranker 成功案例"（2 條記憶）
     → 提供摘要給小質

小質 → 主持 SBE Workshop
     → 撰寫 features/bge_reranker.feature
     → 識別 10 個核心場景

# Red 階段：小質主導
小質 → 撰寫 19 個測試案例
     → 運行測試驗證失敗
     → 提交 test(TDD-Red): ...

# Green 階段：小程主導
小程 → 實作 BGEReranker 類別
     → 運行測試驗證通過
     → 提交 feat(TDD-Green): ...

# Refactor 階段：小程 + 小架協作
小程 → 重構代碼、新增文檔
小架 → 審查架構、提出建議
小程 → 修正後提交 refactor(TDD-Refactor): ...

# Integration 階段：小數 + 小策協作
小數 → 執行完整檢查、清理目錄
小策 → 撰寫週報、更新 README
小憶 → 記錄成功案例到 EvoMem
```

---

## 🧠 EvoMem 決策樹（整合 CODEX 指南）

```
準備開始新任務？
  │
  ├─ [小憶] 查詢歷史記憶
  │     ├─ query("[模組名稱] 歷史 Bug", n_results=10)
  │     └─ query("[模組名稱] 成功案例", n_results=10)
  │
  ├─ 有相關記憶？
  │     ├─ YES → 讀取摘要 → 追加到任務說明 → 納入測試/設計
  │     └─ NO → 繼續任務
  │
  ├─ 任務執行中
  │     ├─ 發現新缺陷？→ add_memory(type="defect", severity="high/medium/low")
  │     ├─ 發現最佳實踐？→ add_memory(type="best_practice")
  │     └─ 一般資訊？→ 僅記錄於任務報告
  │
  └─ 任務完成後
        ├─ [小憶] 記錄成功案例/學習點
        └─ [小策] 引用記憶 ID 於 REPORT.md
```

### EvoMem 使用範例（Week 2）

```python
# === 任務開始前 ===

# 小憶查詢歷史
results = evomem.query("BGE-M3 embedder 常見錯誤", n_results=5)

# 摘要結果（提供給小質）
"""
查詢結果摘要：
1. 空文本導致 crash（嚴重度：高）
   → 建議：新增 test_embed_empty_text_raises_error()

2. 超長文本未截斷導致 OOM（嚴重度：中）
   → 建議：新增 test_embed_long_text_truncates()

3. 批次處理效能問題（嚴重度：低）
   → 建議：新增 test_batch_processing_performance()
"""

# === 任務執行中 ===

# 發現新問題：Windows pytest torchvision access violation
# 小憶記錄學習點
evomem.add_memory(
    content="Windows 環境 pytest 遇到 torchvision access violation 錯誤。解決方案：使用獨立驗證腳本取代 pytest。",
    metadata={
        "type": "learning",
        "severity": "medium",
        "tags": ["Windows", "pytest", "workaround"]
    }
)

# === 任務完成後 ===

# 小憶記錄成功案例
evomem.add_memory(
    content="BGE-M3 Embedder 實作成功：19 個測試全部通過，覆蓋率 85.3%，複雜度 1.18。",
    metadata={
        "project": "Mem0Evomem",
        "type": "success_case",
        "task_id": "Week2-BGE-M3-Embedder",
        "evidence": "tests/unit/test_bge_m3.py, src/embeddings/bge_m3.py"
    }
)
```

---

## 📊 上下文 / Token 管理策略（來自 CODEX 指南）

### 核心原則
- **文檔化交接**：每個角色完成任務後，將要點寫入專屬檔案，後續僅引用「摘要 + 檔案路徑」
- **資料來源附註**：使用網路或 EvoMem 查詢時，列出 `來源：<URL|memory_id>`
- **EvoMem/Cache**：重複資訊存入 `data/project_memory/*.jsonl` 或 `docs/EVOMEM_CACHE.md`
- **階段性摘要**：小秘在每個階段收斂 2-3 行結論，其他角色可引用摘要
- **必要資訊原則**：描述與既有文檔重複時，改為「請參考 <檔案路徑> 第 X 節」

### 實踐範例

**❌ 錯誤做法**（浪費 Token）：
```
小質：「根據之前小研在 docs/research/industry.md 中提到的市場需求，包括：
1. 中文語義搜索需求量大
2. 向量維度需求 1024 維
3. 效能要求 <100ms
4. 相容性要求支援 CPU
......（1000+ 字重複內容）」
```

**✅ 正確做法**（節省 Token）：
```
小質：「根據小研的研究（docs/research/industry.md §2.3），市場需求摘要：
- 中文語義搜索
- 1024 維向量
- <100ms 效能
- CPU 相容性

完整需求請參考該文檔 §2.3 節。」
```

### Token 監控（來自 CLAUDE.md）

```
目前 Token 使用: 70,915 / 200,000 (35.5%)
狀態: 🟢 綠燈（正常使用）

建議：
- 繼續使用當前策略（引用文檔而非重述）
- 小憶查詢結果僅提供摘要（前 3 條記憶）
- 完整內容寫入 docs/EVOMEM_CACHE.md
```

---

## ✅ 任務前檢查清單（必須逐項確認）

> **來自 CODEX 指南 §6**：未勾選完畢前，禁止開始任務

### Phase 0: 前商業階段
- [ ] PRD 已完成（`docs/product/prd.md`）
- [ ] 架構設計已審查（`ARCHITECTURE.md`）
- [ ] 所有依賴已識別
- [ ] 風險已評估

### Phase 1: SBE 階段
- [ ] 小憶已查詢歷史記憶（Bug + 成功案例）
- [ ] `.feature` 文件涵蓋所有核心場景
- [ ] 提供具體範例（Examples Table）
- [ ] SBE workshop 筆記已記錄

### Phase 2: Red 階段
- [ ] 測試基於 `.feature` 撰寫（AAA 格式）
- [ ] EvoMem 缺陷模式已納入測試
- [ ] 測試正確失敗（紅燈）
- [ ] Commit 訊息符合規範（`test(TDD-Red): ...`）

### Phase 3: Green 階段
- [ ] 實作讓所有測試通過（綠燈）
- [ ] 未過度設計（最小實作原則）
- [ ] Commit 訊息符合規範（`feat(TDD-Green): ...`）

### Phase 4: Refactor 階段
- [ ] 複雜度 C ≤ 1.25（radon cc）
- [ ] 型別檢查通過（mypy --strict）
- [ ] Linting 無警告（flake8 + ruff）
- [ ] 測試覆蓋率 ≥ 80%
- [ ] 文檔字串完整
- [ ] 所有測試仍然通過（迴歸測試）
- [ ] Commit 訊息符合規範（`refactor(TDD-Refactor): ...`）

### Phase 5: Review 階段
- [ ] 小架架構審查完成
- [ ] 小質測試審查完成
- [ ] `CODE_REVIEW.md` 已更新
- [ ] 審查建議已納入或記錄

### Phase 6: Integration 階段
- [ ] 完整檢查腳本通過（`./scripts/ci/full_check.sh`）
- [ ] `README.md` 已更新
- [ ] `CHANGELOG.md` 已更新
- [ ] `REPORT.md` 已撰寫
- [ ] EvoMem 記憶已更新（小憶）
- [ ] Git 推送完成（`git push origin main`）

---

## 🔗 相關文檔

### 專案文檔
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - TDD 技術指南（18,000+ 字）
- [WEEK1_FINAL_REPORT.md](WEEK1_FINAL_REPORT.md) - Week 1 完成報告
- [CHANGELOG.md](CHANGELOG.md) - 開發日誌

### 工作區文檔
- [CLAUDE.md](../CLAUDE.md) - 工作區層級規範
- [CODEX啟動指南](../CODEX啟動指南_v1.0.md) - 原始 Codex 框架

### 架構文檔
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系統架構設計（待完成）

---

## 📝 版本歷史

- **v1.0** (2025-11-14): 初始版本
  - 整合 CODEX 啟動指南 v1.0
  - 整合 CLAUDE.md v3.5
  - 針對 Mem0Evomem 專案客製化
  - 新增完整開發流程（Phase 0-6）
  - 新增多專家角色矩陣
  - 新增 EvoMem 決策樹
  - 新增任務前檢查清單

---

**⚡ 使用方式**：

1. **新任務開始時**：閱讀本文件 §Phase 0-1
2. **開發過程中**：依照 §Phase 2-4 TDD 流程
3. **審查與整合**：參考 §Phase 5-6 檢查清單
4. **召喚專家**：查看 §多專家角色矩陣
5. **記憶管理**：使用 §EvoMem 決策樹

**🎯 核心價值**：

- ✅ **自動化**：減少手動重複工作
- ✅ **規範化**：統一開發流程與品質標準
- ✅ **記憶化**：EvoMem 累積經驗避免重複錯誤
- ✅ **協作化**：多專家各司其職提高效率
- ✅ **文檔化**：完整記錄便於知識傳承

---

*Last Updated: 2025-11-14*
*Version: 1.0*
*Maintainer: Mem0Evomem Team + zycaskevin*
