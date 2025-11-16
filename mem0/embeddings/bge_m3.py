"""BGE-M3 中文 Embedder 實作 - TDD Refactor Phase (優化版)

基於 BAAI/bge-m3 模型實現 1024 維中文語義向量嵌入
符合 features/bge_m3.feature 的所有行為規格

Author: EvoMem Team
License: Apache 2.0
"""

import logging
from typing import List, Optional, cast
from FlagEmbedding import BGEM3FlagModel  # type: ignore[import-untyped]

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.base import EmbeddingBase

# 配置日誌
logger = logging.getLogger(__name__)


class BGEM3Embedding(EmbeddingBase):
    """BGE-M3 中文文本嵌入器 (mem0 集成版本)

    將中文文本轉換為 1024 維語義向量，支援語義搜索和相似度計算。

    Constants:
        DEFAULT_BATCH_SIZE: 默認批次大小 (256)
        CHAR_TO_TOKEN_RATIO: 中文字符到 token 的粗略轉換比例 (0.67)
                            基於假設: 1 token ≈ 1.5 個中文字 (1/1.5 = 0.67)

    特性:
    - 模型: BAAI/bge-m3
    - 向量維度: 1024
    - 最大序列長度: 8192 tokens (可配置)
    - 精度: FP16 (可配置)
    - 設備: CPU/GPU (可配置)
    - 中文優化: 針對中文語義理解進行優化

    範例:
        >>> config = BaseEmbedderConfig(model="BAAI/bge-m3")
        >>> embedder = BGEM3Embedding(config)
        >>> vector = embedder.embed("這是一個測試句子")
        >>> len(vector)
        1024
    """

    # 類常量
    DEFAULT_BATCH_SIZE = 256
    CHAR_TO_TOKEN_RATIO = 0.67  # 1 token ≈ 1.5 字

    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        """初始化 BGE-M3 Embedder

        Args:
            config: Embedder 配置對象

        Raises:
            Exception: 當模型載入失敗時
        """
        super().__init__(config)

        # 從 config 讀取參數，提供默認值
        self.config.model = self.config.model or "BAAI/bge-m3"
        self.config.embedding_dims = 1024  # BGE-M3 固定維度

        # 從 model_kwargs 讀取額外參數
        model_kwargs = self.config.model_kwargs or {}
        use_fp16 = model_kwargs.get("use_fp16", True)
        device = model_kwargs.get("device", "cpu")
        max_length = model_kwargs.get("max_length", 8192)

        self.model_name = self.config.model
        self.use_fp16 = use_fp16
        self.device = device
        self.max_length = max_length

        # 載入 BGE-M3 模型
        logger.info(f"Loading {self.model_name} with FP16={use_fp16} on {device}")
        try:
            # type: Any due to FlagEmbedding missing type stubs
            self.model = BGEM3FlagModel(
                self.model_name,
                use_fp16=use_fp16,
                device=device
            )
            logger.info("BGE-M3 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BGE-M3 model: {e}")
            raise

    def _validate_texts(self, texts: List[str]) -> None:
        """驗證文本列表

        Args:
            texts: 待驗證的文本列表

        Raises:
            ValueError: 當文本列表為空或包含空字串時

        Warning:
            當文本長度超過 max_length 時發出警告
        """
        # 檢查空文本
        if not texts or any(not t or not t.strip() for t in texts):
            raise ValueError("不能嵌入空文本")

        # 檢查文本長度
        for i, t in enumerate(texts):
            estimated_tokens = len(t) * self.CHAR_TO_TOKEN_RATIO
            if estimated_tokens > self.max_length:
                logger.warning(
                    f"第 {i+1} 個文本長度 ({len(t)} 字) 可能超過 "
                    f"{self.max_length} tokens，將自動截斷"
                )

    def embed(self, text: str) -> List[float]:
        """嵌入單個文本為 1024 維向量

        Args:
            text: 待嵌入的文本

        Returns:
            1024 維向量 (List[float])

        Raises:
            ValueError: 當文本為空時
            Exception: 當嵌入過程失敗時

        範例:
            >>> vec = embedder.embed("人工智慧正在改變世界")
            >>> len(vec)
            1024
        """
        # 驗證輸入
        self._validate_texts([text])

        # 嵌入文本
        try:
            result = self.model.encode(
                [text],
                batch_size=1,
                max_length=self.max_length
            )
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

        # 返回結果 (符合 List[float] 類型)
        return cast(List[float], result['dense_vecs'][0].tolist())

    def batch_embed(
        self,
        texts: List[str],
        batch_size: int = DEFAULT_BATCH_SIZE
    ) -> List[List[float]]:
        """批次嵌入多個文本

        Args:
            texts: 待嵌入的文本列表
            batch_size: 批次大小，默認 256

        Returns:
            向量列表，每個向量為 1024 維 (List[List[float]])

        Raises:
            ValueError: 當文本列表為空或包含空文本時
            Exception: 當嵌入過程失敗時

        範例:
            >>> vecs = embedder.batch_embed(["文本1", "文本2", "文本3"])
            >>> len(vecs)
            3
            >>> len(vecs[0])
            1024
        """
        # 處理空列表
        if not texts:
            return []

        # 驗證輸入
        self._validate_texts(texts)

        # 批次嵌入
        try:
            result = self.model.encode(
                texts,
                batch_size=batch_size,
                max_length=self.max_length
            )
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            raise

        # 返回結果 (符合 List[List[float]] 類型)
        return cast(
            List[List[float]],
            [vec.tolist() for vec in result['dense_vecs']]
        )

    def __repr__(self) -> str:
        """字串表示"""
        return (
            f"BGEM3Embedding("
            f"model={self.model_name}, "
            f"dims={self.embedding_dims}, "
            f"device={self.device})"
        )
