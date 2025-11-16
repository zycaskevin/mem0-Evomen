import sys
print("Step 1: Python works")

try:
    import FlagEmbedding
    print("Step 2: FlagEmbedding imported")
except Exception as e:
    print(f"Step 2 FAILED: {e}")
    sys.exit(1)

try:
    from FlagEmbedding import BGEM3FlagModel
    print("Step 3: BGEM3FlagModel imported")
except Exception as e:
    print(f"Step 3 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All imports successful!")
