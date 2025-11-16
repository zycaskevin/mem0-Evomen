"""BGE-M3 中文 Embedder 實作 - TDD Green Phase

基於 BAAI/bge-m3 模型實現 1024 維中文語義向量嵌入
符合 features/bge_m3.feature 的所有行為規格
"""

import logging
from typing import List, Optional, cast
from FlagEmbedding import BGEM3FlagModel  # type: ignore[import-untyped]

# 配置日誌
logger = logging.getLogger(__name__)


class BGEM3Embedding:
    """BGE-M3 中文文本嵌入器

    將中文文本轉換為 1024 維語義向量，支援語義搜索和相似度計算。

    特性:
    - 模型: BAAI/bge-m3
    - 向量維度: 1024
    - 最大序列長度: 8192 tokens
    - 精度: FP16
    - 設備: CPU（相容性優先）

    範例:
        >>> embedder = BGEM3Embedding()
        >>> vector = embedder.embed("這是一個測試句子")
        >>> len(vector)
        1024
        >>> vectors = embedder.batch_embed(["文本1", "文本2"])
        >>> len(vectors)
        2
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        use_fp16: bool = True,
        device: str = "cpu",
        max_length: int = 8192
    ):
        """初始化 BGE-M3 Embedder

        Args:
            model_name: 模型名稱，默認 "BAAI/bge-m3"
            use_fp16: 是否使用 FP16 精度，默認 True（提高效能）
            device: 運行設備，默認 "cpu"（相容性優先）
            max_length: 最大序列長度，默認 8192
        """
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.device = device
        self.max_length = max_length

        # 載入模型
        logger.info(f"Loading {model_name} with FP16={use_fp16} on {device}")
        self.model = BGEM3FlagModel(
            model_name,
            use_fp16=use_fp16,
            device=device
        )
        logger.info("Model loaded successfully")

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
            >>> vector = embedder.embed("人工智慧正在改變世界")
            >>> len(vector)
            1024
            >>> all(-1 <= x <= 1 for x in vector)
            True
        """
        # 驗證輸入
        if not text or not text.strip():
            raise ValueError("不能嵌入空文本")

        # 檢查文本長度（粗略估計：1 token ≈ 1.5 字）
        estimated_tokens = len(text) * 0.67
        if estimated_tokens > self.max_length:
            logger.warning(
                f"文本長度 ({len(text)} 字) 可能超過 {self.max_length} tokens，"
                f"將自動截斷"
            )

        # 嵌入文本
        result = self.model.encode(
            [text],
            batch_size=1,
            max_length=self.max_length
        )

        # 返回第一個向量（轉為 Python list）
        return cast(List[float], result['dense_vecs'][0].tolist())

    def _validate_texts(self, texts: List[str]) -> None:
        """驗證文本列表，確保所有文本非空

        Args:
            texts: 待驗證的文本列表

        Raises:
            ValueError: 當任何文本為空時
        """
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"第 {i+1} 個文本為空，不能嵌入空文本")

    def batch_embed(
        self,
        texts: List[str],
        batch_size: int = 256
    ) -> List[List[float]]:
        """批次嵌入多個文本

        Args:
            texts: 待嵌入的文本列表
            batch_size: 批次大小，默認 256（效能優化）

        Returns:
            向量列表，每個向量為 1024 維浮點數列表

        範例:
            >>> embedder = BGEM3Embedding()
            >>> vectors = embedder.batch_embed([
            ...     "人工智慧正在改變世界",
            ...     "機器學習是 AI 的核心技術",
            ...     "深度學習推動了 AI 的發展"
            ... ])
            >>> len(vectors)
            3
            >>> all(len(v) == 1024 for v in vectors)
            True
        """
        # 處理空列表
        if not texts:
            return []

        # 驗證所有文本非空
        self._validate_texts(texts)

        # 批次嵌入
        result = self.model.encode(
            texts,
            batch_size=batch_size,
            max_length=self.max_length
        )

        # 返回所有向量（轉為 Python list）
        return cast(List[List[float]], [vec.tolist() for vec in result['dense_vecs']])

    def __repr__(self) -> str:
        """字串表示"""
        return (
            f"BGEM3Embedding("
            f"model={self.model_name}, "
            f"fp16={self.use_fp16}, "
            f"device={self.device}, "
            f"max_length={self.max_length})"
        )
