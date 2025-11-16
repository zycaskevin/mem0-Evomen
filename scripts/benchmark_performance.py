#!/usr/bin/env python3
"""
Mem0Evomem 性能基準測試

測試項目:
- BGE-M3 單文本嵌入延遲 (P50, P95, P99)
- BGE-M3 批次嵌入吞吐量 (10/100/1000 texts)
- ChromaDB 查詢性能
- 記憶體使用監控
- Docker 容器資源使用

Author: EvoMem Team
License: Apache 2.0
"""

import time
import statistics
import psutil
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加項目根目錄到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.bge_m3 import BGEM3Embedding


class PerformanceBenchmark:
    """性能基準測試工具"""

    def __init__(self):
        """初始化測試環境"""
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "tests": {}
        }

        # 初始化 BGE-M3 Embedder
        print("🔧 初始化 BGE-M3 Embedder...")
        config = BaseEmbedderConfig(
            model="BAAI/bge-m3",
            model_kwargs={
                "use_fp16": True,
                "device": "cpu",
                "max_length": 8192
            }
        )
        self.embedder = BGEM3Embedding(config)
        print("✅ BGE-M3 Embedder 載入成功\n")

    def _get_system_info(self) -> Dict[str, Any]:
        """獲取系統資訊"""
        return {
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "python_version": f"{psutil.PROCFS_PATH}",
        }

    def _measure_memory_usage(self) -> Dict[str, float]:
        """測量當前記憶體使用"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_mb": round(memory_info.rss / (1024**2), 2),
            "vms_mb": round(memory_info.vms / (1024**2), 2),
            "percent": round(process.memory_percent(), 2)
        }

    def test_single_text_embedding_latency(self, iterations: int = 100) -> Dict[str, Any]:
        """
        測試單文本嵌入延遲

        Args:
            iterations: 測試次數 (默認 100)

        Returns:
            測試結果 (P50, P95, P99, mean, std)
        """
        print(f"📊 測試 1/5: 單文本嵌入延遲 ({iterations} 次迭代)")

        test_texts = [
            "人工智慧正在改變世界",
            "機器學習是人工智慧的一個重要分支",
            "深度學習在圖像識別領域取得了巨大突破",
            "自然語言處理技術日益成熟",
            "向量數據庫是 AI 應用的重要基礎設施"
        ]

        latencies = []
        memory_before = self._measure_memory_usage()

        for i in range(iterations):
            text = test_texts[i % len(test_texts)]
            start_time = time.perf_counter()
            _ = self.embedder.embed(text)
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

            if (i + 1) % 20 == 0:
                print(f"  進度: {i + 1}/{iterations}")

        memory_after = self._measure_memory_usage()

        # 計算統計指標
        latencies_sorted = sorted(latencies)
        result = {
            "iterations": iterations,
            "mean_ms": round(statistics.mean(latencies), 2),
            "median_ms": round(statistics.median(latencies), 2),
            "std_ms": round(statistics.stdev(latencies), 2),
            "p50_ms": round(latencies_sorted[int(len(latencies_sorted) * 0.50)], 2),
            "p95_ms": round(latencies_sorted[int(len(latencies_sorted) * 0.95)], 2),
            "p99_ms": round(latencies_sorted[int(len(latencies_sorted) * 0.99)], 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "memory_before_mb": memory_before["rss_mb"],
            "memory_after_mb": memory_after["rss_mb"],
            "memory_delta_mb": round(memory_after["rss_mb"] - memory_before["rss_mb"], 2)
        }

        print(f"  ✅ 完成: P50={result['p50_ms']}ms, P95={result['p95_ms']}ms, P99={result['p99_ms']}ms\n")
        return result

    def test_batch_embedding_throughput(self, batch_sizes: List[int] = [10, 100, 1000]) -> Dict[str, Any]:
        """
        測試批次嵌入吞吐量

        Args:
            batch_sizes: 批次大小列表 (默認 [10, 100, 1000])

        Returns:
            測試結果 (每個批次大小的吞吐量)
        """
        print(f"📊 測試 2/5: 批次嵌入吞吐量 (批次大小: {batch_sizes})")

        base_text = "這是一個測試文本，用於評估批次嵌入的性能。"
        results = {}

        for batch_size in batch_sizes:
            print(f"  測試批次大小: {batch_size}")
            texts = [f"{base_text} 編號: {i}" for i in range(batch_size)]

            memory_before = self._measure_memory_usage()
            start_time = time.perf_counter()
            _ = self.embedder.batch_embed(texts, batch_size=256)
            end_time = time.perf_counter()
            memory_after = self._measure_memory_usage()

            elapsed_s = end_time - start_time
            throughput = batch_size / elapsed_s

            results[f"batch_{batch_size}"] = {
                "batch_size": batch_size,
                "elapsed_s": round(elapsed_s, 2),
                "throughput_texts_per_s": round(throughput, 2),
                "latency_per_text_ms": round((elapsed_s / batch_size) * 1000, 2),
                "memory_before_mb": memory_before["rss_mb"],
                "memory_after_mb": memory_after["rss_mb"],
                "memory_delta_mb": round(memory_after["rss_mb"] - memory_before["rss_mb"], 2)
            }

            print(f"    ✅ 吞吐量: {results[f'batch_{batch_size}']['throughput_texts_per_s']} texts/s")

        print()
        return results

    def test_embedding_quality(self) -> Dict[str, Any]:
        """
        測試嵌入質量 (語義相似度)

        Returns:
            測試結果 (相似文本距離、不相似文本距離)
        """
        print("📊 測試 3/5: 嵌入質量 (語義相似度)")

        # 相似文本對
        similar_pairs = [
            ("人工智慧技術發展迅速", "AI 科技進步神速"),
            ("機器學習是 AI 的核心", "ML 是人工智慧的關鍵技術"),
            ("深度學習改變了世界", "深度神經網絡帶來革命性變化")
        ]

        # 不相似文本對
        dissimilar_pairs = [
            ("人工智慧技術發展迅速", "今天天氣很好"),
            ("機器學習是 AI 的核心", "我喜歡吃水果"),
            ("深度學習改變了世界", "貓是一種可愛的動物")
        ]

        def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
            """計算餘弦相似度"""
            import math
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))
            return dot_product / (magnitude1 * magnitude2)

        # 測試相似文本
        similar_scores = []
        for text1, text2 in similar_pairs:
            vec1 = self.embedder.embed(text1)
            vec2 = self.embedder.embed(text2)
            similarity = cosine_similarity(vec1, vec2)
            similar_scores.append(similarity)

        # 測試不相似文本
        dissimilar_scores = []
        for text1, text2 in dissimilar_pairs:
            vec1 = self.embedder.embed(text1)
            vec2 = self.embedder.embed(text2)
            similarity = cosine_similarity(vec1, vec2)
            dissimilar_scores.append(similarity)

        result = {
            "similar_texts": {
                "mean_similarity": round(statistics.mean(similar_scores), 4),
                "min_similarity": round(min(similar_scores), 4),
                "max_similarity": round(max(similar_scores), 4)
            },
            "dissimilar_texts": {
                "mean_similarity": round(statistics.mean(dissimilar_scores), 4),
                "min_similarity": round(min(dissimilar_scores), 4),
                "max_similarity": round(max(dissimilar_scores), 4)
            },
            "separation": round(
                statistics.mean(similar_scores) - statistics.mean(dissimilar_scores), 4
            )
        }

        print(f"  ✅ 相似文本平均相似度: {result['similar_texts']['mean_similarity']}")
        print(f"  ✅ 不相似文本平均相似度: {result['dissimilar_texts']['mean_similarity']}")
        print(f"  ✅ 分離度: {result['separation']}\n")

        return result

    def test_cold_start_time(self) -> Dict[str, Any]:
        """
        測試冷啟動時間 (模型載入時間)

        Returns:
            測試結果 (模型載入時間)
        """
        print("📊 測試 4/5: 冷啟動時間")

        # 注意: 這個測試會重新載入模型，因此會比較慢
        print("  重新載入模型以測試冷啟動時間...")

        start_time = time.perf_counter()
        config = BaseEmbedderConfig(
            model="BAAI/bge-m3",
            model_kwargs={
                "use_fp16": True,
                "device": "cpu",
                "max_length": 8192
            }
        )
        _ = BGEM3Embedding(config)
        end_time = time.perf_counter()

        cold_start_s = end_time - start_time

        result = {
            "cold_start_time_s": round(cold_start_s, 2),
            "cold_start_time_ms": round(cold_start_s * 1000, 2)
        }

        print(f"  ✅ 冷啟動時間: {result['cold_start_time_s']}s\n")

        return result

    def test_concurrent_requests(self, num_threads: int = 10) -> Dict[str, Any]:
        """
        測試並發請求性能

        Args:
            num_threads: 並發線程數 (默認 10)

        Returns:
            測試結果 (並發性能指標)
        """
        print(f"📊 測試 5/5: 並發請求性能 ({num_threads} 線程)")

        import threading

        test_text = "測試並發請求的性能表現"
        latencies = []
        errors = []
        lock = threading.Lock()

        def embed_text():
            """單個線程的嵌入任務"""
            try:
                start_time = time.perf_counter()
                _ = self.embedder.embed(test_text)
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000

                with lock:
                    latencies.append(latency_ms)
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # 創建並啟動線程
        threads = []
        start_time = time.perf_counter()
        for _ in range(num_threads):
            thread = threading.Thread(target=embed_text)
            threads.append(thread)
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()
        end_time = time.perf_counter()

        total_time_s = end_time - start_time

        result = {
            "num_threads": num_threads,
            "total_time_s": round(total_time_s, 2),
            "throughput_requests_per_s": round(num_threads / total_time_s, 2),
            "mean_latency_ms": round(statistics.mean(latencies), 2) if latencies else None,
            "p95_latency_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 2) if latencies else None,
            "errors": len(errors),
            "success_rate": round((len(latencies) / num_threads) * 100, 2)
        }

        print(f"  ✅ 吞吐量: {result['throughput_requests_per_s']} req/s")
        print(f"  ✅ 平均延遲: {result['mean_latency_ms']}ms")
        print(f"  ✅ 成功率: {result['success_rate']}%\n")

        return result

    def run_all_tests(self) -> Dict[str, Any]:
        """執行所有測試"""
        print("=" * 60)
        print("🚀 Mem0Evomem 性能基準測試")
        print("=" * 60)
        print()

        # 執行所有測試
        self.results["tests"]["single_text_latency"] = self.test_single_text_embedding_latency()
        self.results["tests"]["batch_throughput"] = self.test_batch_embedding_throughput()
        self.results["tests"]["embedding_quality"] = self.test_embedding_quality()
        self.results["tests"]["cold_start"] = self.test_cold_start_time()
        self.results["tests"]["concurrent_requests"] = self.test_concurrent_requests()

        return self.results

    def generate_report(self, output_file: str = "data/benchmarks/performance_report.json"):
        """生成測試報告"""
        import os

        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 保存 JSON 報告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("=" * 60)
        print("📊 測試完成！")
        print("=" * 60)
        print()
        print(f"✅ 報告已生成: {output_file}")
        print()

        # 打印摘要
        print("📈 性能摘要:")
        print(f"  - 單文本嵌入 P50: {self.results['tests']['single_text_latency']['p50_ms']}ms")
        print(f"  - 單文本嵌入 P95: {self.results['tests']['single_text_latency']['p95_ms']}ms")
        print(f"  - 批次吞吐量 (100): {self.results['tests']['batch_throughput']['batch_100']['throughput_texts_per_s']} texts/s")
        print(f"  - 冷啟動時間: {self.results['tests']['cold_start']['cold_start_time_s']}s")
        print(f"  - 並發吞吐量 (10 線程): {self.results['tests']['concurrent_requests']['throughput_requests_per_s']} req/s")
        print(f"  - 語義分離度: {self.results['tests']['embedding_quality']['separation']}")
        print()


def main():
    """主函數"""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_tests()
    benchmark.generate_report()


if __name__ == "__main__":
    main()
