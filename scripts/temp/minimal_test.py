import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Step 1: Import dependencies")
try:
    import numpy as np
    from FlagEmbedding import BGEM3FlagModel
    print("OK - Dependencies imported")
except Exception as e:
    print(f"FAIL - Dependencies: {e}")
    sys.exit(1)

print("\nStep 2: Import BGEM3Embedding")
try:
    from src.embeddings.bge_m3 import BGEM3Embedding
    print("OK - BGEM3Embedding imported")
except Exception as e:
    print(f"FAIL - Import: {e}")
    sys.exit(1)

print("\nStep 3: Create instance (loading model...)")
try:
    embedder = BGEM3Embedding()
    print("OK - Instance created")
except Exception as e:
    print(f"FAIL - Instance: {e}")
    sys.exit(1)

print("\nStep 4: Test embed()")
try:
    result = embedder.embed("test")
    assert len(result) == 1024
    print(f"OK - embed() returned {len(result)} dimensions")
except Exception as e:
    print(f"FAIL - embed(): {e}")
    sys.exit(1)

print("\nStep 5: Test empty text error")
try:
    embedder.embed("")
    print("FAIL - Should raise ValueError")
    sys.exit(1)
except ValueError as e:
    if "empty" in str(e).lower() or "空" in str(e):
        print("OK - Empty text raises ValueError")
    else:
        print(f"FAIL - Wrong error: {e}")
        sys.exit(1)

print("\nStep 6: Test batch_embed()")
try:
    results = embedder.batch_embed(["a", "b", "c"])
    assert len(results) == 3
    print(f"OK - batch_embed() returned {len(results)} vectors")
except Exception as e:
    print(f"FAIL - batch_embed(): {e}")
    sys.exit(1)

print("\nStep 7: Test config")
try:
    assert embedder.model_name == "BAAI/bge-m3"
    assert embedder.use_fp16 == True
    assert embedder.device == "cpu"
    assert embedder.max_length == 8192
    print("OK - Config verified")
except AssertionError as e:
    print(f"FAIL - Config: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("SUCCESS - All tests passed!")
print("="*60)
print("\nNext step: git commit -m 'feat(TDD-Green): Implement BGE-M3 Embedder'")
