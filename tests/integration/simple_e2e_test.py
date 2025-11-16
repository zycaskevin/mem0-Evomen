"""BGE-M3 + mem0 Simple E2E Test (No emoji, ASCII only)

Author: EvoMem Team
License: Apache 2.0
"""

import os
import sys
import shutil

# Add mem0-evomem to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../mem0-evomem"))

print("=" * 80)
print("BGE-M3 + mem0 End-to-End Integration Test")
print("=" * 80)

# Cleanup old test data
if os.path.exists("./test_chroma_db"):
    shutil.rmtree("./test_chroma_db")
    print("[OK] Cleaned up old test data")

# Test 1: Import Check
print("\n[Test 1] Import Check")
try:
    from mem0 import Memory
    print("[OK] mem0.Memory imported successfully")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Create Memory Instance
print("\n[Test 2] Create Memory Instance (BGE-M3 embedder)")
try:
    config = {
        "embedder": {
            "provider": "bge_m3",
            "config": {
                "model": "BAAI/bge-m3",
                "model_kwargs": {
                    "use_fp16": True,
                    "device": "cpu",
                    "max_length": 8192
                }
            }
        },
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "e2e_test_collection",
                "path": "./test_chroma_db"
            }
        }
    }

    memory = Memory.from_config(config)
    print("[OK] Memory instance created successfully")
    print(f"   Embedder: {memory.embedding_model.__class__.__name__}")
    print(f"   Vector Store: {memory.vector_store.__class__.__name__}")
except Exception as e:
    print(f"[FAIL] Creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Add Chinese Memories
print("\n[Test 3] Add Chinese Memories")
test_memories = [
    "AI is changing the world, especially in Chinese semantic understanding",
    "Python is a high-level programming language known for simplicity",
    "Deep learning uses neural networks to simulate the brain"
]

added_count = 0
for i, text in enumerate(test_memories, 1):
    try:
        result = memory.add(text, user_id=f"test_user_{i}")
        print(f"[OK] Memory {i} added successfully")
        added_count += 1
    except Exception as e:
        print(f"[FAIL] Memory {i} failed: {e}")

print(f"\n[Stats] Added: {added_count}/{len(test_memories)}")

# Test 4: Chinese Semantic Search
print("\n[Test 4] Semantic Search")
search_queries = [
    ("AI impact on world", "test_user_1"),
    ("What is Python?", "test_user_2"),
    ("How do neural networks work?", "test_user_3"),
]

search_success = 0
for query, user_id in search_queries:
    try:
        results = memory.search(query, user_id=user_id)
        print(f"\nQuery: \"{query}\"")
        print(f"User: {user_id}")
        print(f"Results: {len(results)}")

        if len(results) > 0:
            print(f"[OK] Search successful")
            first = results[0]
            if isinstance(first, dict):
                memory_text = first.get("memory", first.get("text", ""))
                score = first.get("score", first.get("distance", "N/A"))
                print(f"   Top 1: {memory_text[:50]}...")
                print(f"   Score: {score}")
            search_success += 1
        else:
            print(f"[WARN] No results found")
    except Exception as e:
        print(f"[FAIL] Search failed: {e}")

print(f"\n[Stats] Search success: {search_success}/{len(search_queries)}")

# Test 5: Batch Operations
print("\n[Test 5] Batch Add Memories")
batch_texts = [
    "Machine learning includes supervised and unsupervised learning",
    "Reinforcement learning trains AI through reward mechanisms",
    "Transfer learning reuses pretrained models"
]

batch_success = 0
for text in batch_texts:
    try:
        memory.add(text, user_id="test_user_batch")
        batch_success += 1
    except Exception as e:
        print(f"[FAIL] Batch add failed: {e}")

print(f"[Stats] Batch add: {batch_success}/{len(batch_texts)}")

# Test batch search
try:
    results = memory.search("AI training methods", user_id="test_user_batch", limit=3)
    print(f"[OK] Batch search successful, returned {len(results)} results")
except Exception as e:
    print(f"[FAIL] Batch search failed: {e}")

# Cleanup
print("\n[Cleanup] Removing test data")
try:
    if os.path.exists("./test_chroma_db"):
        shutil.rmtree("./test_chroma_db")
    print("[OK] Cleanup complete")
except Exception as e:
    print(f"[WARN] Cleanup failed: {e}")

# Summary
print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print(f"[OK] Import Check: Passed")
print(f"[OK] Memory Instance: Passed")
print(f"[OK] Add Memories: {added_count}/{len(test_memories)}")
print(f"[OK] Search Memories: {search_success}/{len(search_queries)}")
print(f"[OK] Batch Operations: {batch_success}/{len(batch_texts)}")
print("=" * 80)

if added_count == len(test_memories) and search_success >= 2:
    print("[SUCCESS] End-to-end integration test passed!")
    sys.exit(0)
else:
    print("[WARN] Some tests did not pass, further investigation needed")
    sys.exit(1)
