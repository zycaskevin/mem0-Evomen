# Mem0Evomem 專案開發指南

**版本**: v2.0 (基於 WORKSPACE_SPEC v4.0)  
**創建日期**: 2025-11-16  
**專案**: Mem0Evomem - 全球最強中文 AI 記憶系統  
**基於**: [mem0](https://github.com/mem0ai/mem0) (Apache 2.0)

---

## 🎯 專案概述

Mem0Evomem 是基於 mem0 的 Fork 專案，專注於**中文優化**和**性能提升**。

### 核心目標
- **中文準確度**: 44% → 95%+ (+116%)
- **功能完整性**: 40% → 93%+ (+133%)
- **100% 向後兼容**: 完全相容 mem0 API
- **實施時間**: 6 週完成

### 技術策略
- Fork mem0 官方倉庫
- 整合 BGE-M3 Embedder（中文優化）
- 整合 BGE Reranker（複雜查詢優化）
- 僅需 ~140 行代碼 + 2 行修改

---

## 🚨 絕對規則 (來自 WORKSPACE_SPEC v4.0)

### ❌ 禁止事項

```yaml
NEVER:
  - 創建根目錄文件 → 使用 src/ 結構
  - 創建 .md 文件（除非明確要求）
  - 跳過 TDD Red-Green-Refactor 循環
  - 創建重複文件 → 擴展現有文件
  - 使用自由文本交接 → 使用 JSON Schema
  - 跳過來源標註 → 所有事實需來源或標記 [ASSUMPTION]
  - 累積完整歷史 → 每次交接修剪
  - 跳過審查 → 計劃和代碼都必須審查
```

### ✅ 必須遵守

```yaml
MUST:
  - TDD First: Red → Green → Refactor
  - Atomic Commits: 每個階段單獨提交
  - Structured Handoffs: JSON Schema 交接協議
  - Source Attribution: 事實有來源或標記 [ASSUMPTION]
  - Context Pruning: 交接時執行輸入過濾
  - Checkpoint: 階段里程碑時生成檢查點
  - Multi-Model Review: Codex + Gemini 審查計劃/代碼
  - Code Quality: 平均 CC ≤ 5, Coverage ≥ 80%
```

---

## 📋 核心協議 (WORKSPACE_SPEC v4.0)

### 1.1 Agent Handoff Protocol

**規則**: 所有 agent 交接必須使用 JSON Schema

```yaml
Schema: C:\Users\User\.claude\schemas\handoff-v1.json
Fields:
  - schemaVersion: "1.0.0"
  - from: {agentType, timestamp}
  - to: {agentType, requiredContext}
  - summary: {keyFindings, decisions}
  - artifacts: [{type, path, sections}]
  - metadata: {tokensUsed, fullOutputPath}

Constraint:
  - summary.keyFindings: MAX 5 items, each <50 tokens
  - Total handoff JSON: <500 tokens
  - Full output saved to: data/handoffs/{agent}_{timestamp}.json
```

### 1.2 Input Filter Protocol

**規則**: 每次 agent 切換必須執行輸入過濾

```yaml
Filter Process:
  1. 提取相關決策（MAX 5）
  2. 僅列出 artifact 路徑（無內容）
  3. 提取警告
  4. 移除：工具調用、中間討論、重複

Target: <500 tokens after filtering
```

### 1.3 Memory Management Protocol

**規則**: 雙層記憶系統

```yaml
短期上下文:
  Storage: 當前階段對話 + 最近 3 次交接
  Limit: 5,000 tokens
  Action: 每次交接後修剪至 3,000 tokens
  Archive: data/stage_archives/

長期記憶 (EvoMem):
  Storage: 事實、引用、成功/失敗模式
  Retrieval: Temporal KG, Top 3 相關
  Query: memory.query_relevant(query, context, top_k=3)
  Effect: 2K → 300 tokens (85% 減少)
```

### 1.4 Source Attribution Protocol

**規則**: 所有事實性陳述必須有來源或標記 [ASSUMPTION]

```yaml
Format:
  Correct: "市場規模 500 億 [來源: URL]"
  Wrong: "市場規模 500 億" (no source)
  Acceptable: "市場持續成長 [ASSUMPTION: 需驗證]"

Validator: 小查 (Agent #12) auto-checks
```

### 1.5 Checkpoint Protocol

**規則**: 階段完成時生成檢查點

```yaml
Trigger: Stage end (前商業/SBE/TDD/交付)
Format: CHECKPOINT_{stage}.md
Content:
  - Key decisions (with sources)
  - Assumptions to validate
  - Artifacts index
  - Token stats (before/after)
Effect: 40K → 1.25K tokens (97% compression)
```

### 1.6 Review Protocol

**規則**: 計劃和代碼的多模型審查

詳細執行細節參考 `C:\Users\User\.claude\docs\v4.0\REVIEW_PROTOCOL.md`

```yaml
Trigger Points:
  - Plan完成 → 執行審查後才允許進入開發
  - Code完成 → 在 merge / deploy 前完成審查
  - Checkpoint生成 → 驗證交付完整性

Review Flow:
  Step 1: Codex Review
    Output: data/reviews/codex_{type}_{timestamp}.json
    Threshold: overall_score >= 8/10

  Step 2: Gemini Review
    Output: data/reviews/gemini_{type}_{timestamp}.json
    Threshold: overall_score >= 8/10

  Step 3: Cross-Validation
    Compare: codex_review vs gemini_review
    If disagreement: Flag human review + log in CHECKPOINT
    If both pass: Continue
    If any fail: Fix → 重新送審 (兩邊都要重跑)

Review Criteria - Code:
  - Complexity (C <= 1.25)
  - Coverage (>= 80%)
  - Type safety
  - Security vulnerabilities
  - Performance bottlenecks

Storage & Audit:
  - 資料夾: data/reviews/
  - Handoff: 附上 codex+gemini 跑完的檔案路徑
  - Checkpoint: 摘要評分、未解決問題、後續 TODO
```

---

## 🚀 當前任務：Week 2-3 Phase 3 (TDD Refactor)

### 任務清單

1. **類型檢查** (mypy --strict)
2. **複雜度分析** (radon cc, 目標 CC ≤ 1.25)
3. **代碼重構**
4. **代碼審查** (Codex + Gemini)
5. **文檔完善**
6. **Git 提交**

### 下一步行動

```bash
# Step 1: 類型檢查
mypy src/embeddings/bge_m3.py --strict

# Step 2: 複雜度分析
radon cc src/embeddings/bge_m3.py -a -nc

# Step 3: 提交
git add src/embeddings/bge_m3.py
git commit -m "refactor(TDD-Refactor): optimize BGE-M3 embedder"
git push origin evomem-enhanced
```

---

## 📁 專案結構

```
Mem0Evomem/
├── CLAUDE.md                    # 本文件 (專案開發指南)
├── data/                        # 📊 運行時數據 (v4.0 新增)
│   ├── handoffs/               # Agent 交接記錄 (JSON)
│   ├── reviews/                # Codex + Gemini 審查結果
│   ├── stage_archives/         # 階段歸檔
│   └── checkpoints/            # 階段檢查點
├── src/embeddings/bge_m3.py   # BGE-M3 Embedder (已實現)
├── tests/unit/test_bge_m3.py  # 19 tests
└── features/bge_m3.feature    # 19 scenarios
```

---

**維護者**: EvoMem Team  
**許可證**: Apache 2.0 (繼承自 mem0)  
**專案狀態**: ✅ Week 2-3 Phase 3 (TDD Refactor) 準備就緒
