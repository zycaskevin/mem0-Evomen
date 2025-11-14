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

  Scenario: 嵌入空文本應該拋出錯誤
    Given 一個 BGEM3Embedding 實例
    When 我嵌入空文本 ""
    Then 應該拋出 ValueError 異常
    And 異常訊息應該包含 "不能嵌入空文本"

  Scenario: 嵌入超長文本應該自動截斷
    Given 一個 BGEM3Embedding 實例
    When 我嵌入一個超過 8192 token 的長文本
    Then 應該自動截斷到 8192 token
    And 應該返回一個 1024 維的向量
    And 應該記錄警告訊息

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

  Scenario: 批次嵌入空列表應該返回空列表
    Given 一個 BGEM3Embedding 實例
    When 我批次嵌入一個空列表
    Then 應該返回一個空列表
    And 不應該拋出任何異常

  Scenario: 相似文本應該有相似的向量
    Given 一個 BGEM3Embedding 實例
    When 我嵌入文本 "人工智慧"
    And 我嵌入文本 "AI 技術"
    Then 兩個向量的餘弦相似度應該大於 0.7

  Scenario: 不相似文本應該有不同的向量
    Given 一個 BGEM3Embedding 實例
    When 我嵌入文本 "人工智慧"
    And 我嵌入文本 "今天天氣很好"
    Then 兩個向量的餘弦相似度應該小於 0.5

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

  Scenario: 驗證模型配置
    Given 一個 BGEM3Embedding 實例
    Then 模型名稱應該是 "BAAI/bge-m3"
    And 應該使用 FP16 精度
    And 應該運行在 CPU 上
    And 最大序列長度應該是 8192

  Scenario: 多線程並發嵌入
    Given 一個 BGEM3Embedding 實例
    When 我在 4 個線程中同時嵌入不同的文本
    Then 所有嵌入操作都應該成功
    And 返回的向量應該是確定性的（相同文本總是返回相同向量）

  Scenario: 記憶體效能驗證
    Given 一個 BGEM3Embedding 實例
    When 我批次嵌入 100 個文本
    Then 記憶體使用量不應該超過 2GB
    And 所有嵌入操作都應該在 30 秒內完成

  @performance
  Scenario: 批次處理效能優化
    Given 一個 BGEM3Embedding 實例
    When 我使用 batch_size=256 批次嵌入 1000 個文本
    Then 平均每個文本的嵌入時間應該小於 50ms
    And 批次處理應該比逐個處理快至少 5 倍
