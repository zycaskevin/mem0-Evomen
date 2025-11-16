"""
依賴版本兼容性驗證腳本

目的: 驗證 mem0ai 和 FlagEmbedding 的版本兼容性
重要性: ⭐⭐ 中等 - 避免依賴衝突

執行:
    python scripts/verify_dependencies.py
"""

import sys
import subprocess
from pkg_resources import get_distribution, DistributionNotFound


def get_package_version(package_name):
    """獲取已安裝包的版本"""
    try:
        return get_distribution(package_name).version
    except DistributionNotFound:
        return None


def run_pip_check():
    """運行 pip check 檢查依賴衝突"""
    try:
        result = subprocess.run(
            ["pip", "check"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_python_version():
    """檢查 Python 版本 (Meta-Review 補充)"""
    print("=" * 60)
    print("[0/5] 檢查 Python 版本")
    print("=" * 60)
    print()

    major, minor, micro = sys.version_info[:3]
    print(f"Python 版本: {major}.{minor}.{micro}")

    if major < 3:
        print("❌ 需要 Python 3.x")
        print("   請升級到 Python 3.8+")
        return False

    if minor < 8:
        print(f"⚠️ Python {major}.{minor} 版本過舊")
        print("   BGE-M3 和 FlagEmbedding 建議使用 Python 3.8+")
        print("   某些功能可能無法使用")
        print()
        print("建議操作:")
        print("1. 升級 Python: https://www.python.org/downloads/")
        print("2. 或使用 pyenv/conda 管理多個 Python 版本")
        return False
    else:
        print(f"✅ Python {major}.{minor}.{micro} 符合要求 (需要 >=3.8)")

    print()
    return True


def check_platform_compatibility():
    """檢查平台兼容性 (Meta-Review 補充)"""
    import platform

    print("=" * 60)
    print("[0/5] 檢查平台兼容性")
    print("=" * 60)
    print()

    system = platform.system()
    machine = platform.machine()
    release = platform.release()

    print(f"操作系統: {system}")
    print(f"版本: {release}")
    print(f"架構: {machine}")
    print()

    warnings = []

    if system == "Windows":
        print("⚠️ Windows 平台注意事項:")
        print("   1. 某些依賴可能需要 Visual C++ Build Tools")
        print("   2. 建議使用 Anaconda/Miniconda 環境")
        print("   3. 如遇到安裝問題,請查看: https://wiki.python.org/moin/WindowsCompilers")
        warnings.append("Windows 可能需要額外工具")

    elif system == "Darwin":
        print("⚠️ macOS 平台注意事項:")
        if "arm" in machine.lower() or "aarch" in machine.lower():
            print("   1. M1/M2 芯片需要特殊處理")
            print("   2. 建議使用 miniforge 而非 Anaconda")
            print("   3. 某些依賴可能需要從源碼編譯")
            warnings.append("Apple Silicon 可能需要額外配置")
        else:
            print("   1. Intel 芯片兼容性較好")
            print("   2. 建議使用 Homebrew 管理依賴")

    elif system == "Linux":
        print("✅ Linux 平台兼容性最佳")
        print("   - 大多數依賴都有預編譯的 wheel")
        print("   - 建議使用系統包管理器安裝基礎依賴")

    else:
        print(f"⚠️ 未知平台: {system}")
        print("   可能遇到兼容性問題")
        warnings.append(f"未知平台 {system}")

    print()

    if warnings:
        print(f"⚠️ 發現 {len(warnings)} 個平台相關警告")
        return True  # 警告但不阻止繼續
    else:
        print("✅ 平台兼容性檢查通過")
        return True


def verify_dependencies():
    """驗證依賴版本兼容性"""
    print("=" * 60)
    print("依賴版本兼容性驗證")
    print("=" * 60)
    print()

    # 目標依賴
    target_deps = {
        "mem0ai": ">=1.0.0",
        "FlagEmbedding": "==1.3.5",
        "torch": None,  # 檢查但不強制版本
        "transformers": None,
        "numpy": None,
        "pytest": ">=7.0.0",
        "black": ">=23.0.0",
    }

    # Step 1: 檢查已安裝的包
    print("[1/4] 檢查已安裝的包...")
    print()

    installed = {}
    missing = []

    for package, version_req in target_deps.items():
        version = get_package_version(package)
        if version:
            installed[package] = version
            status = "✅"
            if version_req:
                print(f"{status} {package:20} {version:15} (要求: {version_req})")
            else:
                print(f"{status} {package:20} {version:15}")
        else:
            missing.append(package)
            print(f"❌ {package:20} 未安裝          (要求: {version_req or '任意版本'})")

    print()

    if missing:
        print(f"⚠️ 缺少 {len(missing)} 個必要的包")
        print("   請執行: pip install " + " ".join(missing))
        print()

    # Step 2: 檢查關鍵依賴版本
    print("[2/4] 檢查關鍵依賴版本...")
    print()

    issues = []

    # 檢查 mem0ai 版本
    if "mem0ai" in installed:
        mem0_version = installed["mem0ai"]
        major_minor = ".".join(mem0_version.split(".")[:2])
        if float(major_minor) >= 1.0:
            print(f"✅ mem0ai 版本符合要求: {mem0_version} (>=1.0.0)")
        else:
            print(f"❌ mem0ai 版本過舊: {mem0_version} (需要 >=1.0.0)")
            issues.append("mem0ai 版本不符合要求")
    else:
        print("❌ mem0ai 未安裝")
        issues.append("mem0ai 未安裝")

    # 檢查 FlagEmbedding 版本
    if "FlagEmbedding" in installed:
        flag_version = installed["FlagEmbedding"]
        if flag_version == "1.3.5":
            print(f"✅ FlagEmbedding 版本正確: {flag_version}")
        else:
            print(f"⚠️ FlagEmbedding 版本不同: {flag_version} (推薦 1.3.5)")
            print("   可能會有 API 差異，建議測試")
    else:
        print("❌ FlagEmbedding 未安裝")
        issues.append("FlagEmbedding 未安裝")

    # 檢查 torch 版本
    if "torch" in installed:
        torch_version = installed["torch"]
        print(f"✅ PyTorch 版本: {torch_version}")
    else:
        print("⚠️ PyTorch 未安裝（FlagEmbedding 需要）")

    print()

    # Step 3: 運行 pip check
    print("[3/4] 檢查依賴衝突 (pip check)...")
    print()

    success, stdout, stderr = run_pip_check()

    if success:
        print("✅ 無依賴衝突")
    else:
        print("❌ 檢測到依賴衝突:")
        print()
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
        issues.append("存在依賴衝突")

    print()

    # Step 4: 測試 import
    print("[4/4] 測試關鍵包導入...")
    print()

    import_tests = [
        ("mem0", "from mem0 import Memory"),
        ("FlagEmbedding", "from FlagEmbedding import BGEM3FlagModel, FlagReranker"),
        ("torch", "import torch"),
        ("numpy", "import numpy"),
    ]

    import_success = 0
    for name, import_statement in import_tests:
        try:
            exec(import_statement)
            print(f"✅ {name:20} 導入成功")
            import_success += 1
        except Exception as e:
            print(f"❌ {name:20} 導入失敗: {e}")
            issues.append(f"{name} 導入失敗")

    print()

    # 總結
    print("=" * 60)
    if not issues:
        print("✅ 所有依賴檢查通過")
        print("=" * 60)
        print()
        print("依賴環境正常，可以開始開發。")
        return True
    else:
        print("❌ 發現問題")
        print("=" * 60)
        print()
        print("問題清單:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print()
        print("建議修復步驟:")
        print("1. 安裝缺失的包")
        print("2. 升級或降級衝突的包")
        print("3. 創建新的虛擬環境重新安裝")
        return False


def print_installation_guide():
    """打印安裝指南"""
    print()
    print("=" * 60)
    print("推薦的安裝步驟")
    print("=" * 60)
    print()
    print("""
# 1. 創建虛擬環境
python -m venv venv
venv\\Scripts\\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. 升級 pip
python -m pip install --upgrade pip

# 3. 安裝核心依賴
pip install mem0ai>=1.0.0
pip install FlagEmbedding==1.3.5

# 4. 安裝開發依賴
pip install pytest>=7.0.0 pytest-cov>=4.0.0
pip install black>=23.0.0 flake8>=6.0.0 mypy>=1.0.0

# 5. 驗證安裝
python scripts/verify_dependencies.py
""")


def print_dependency_matrix():
    """打印依賴矩陣"""
    print()
    print("=" * 60)
    print("依賴版本矩陣")
    print("=" * 60)
    print()
    print("""
| 包名              | 要求版本    | 推薦版本    | 說明                |
|-------------------|------------|------------|---------------------|
| mem0ai            | >=1.0.0    | 1.0.0      | 核心記憶系統        |
| FlagEmbedding     | ==1.3.5    | 1.3.5      | BGE 模型（固定版本）|
| torch             | 任意       | >=2.0.0    | PyTorch（自動安裝） |
| transformers      | 任意       | >=4.30.0   | Transformers        |
| numpy             | 任意       | >=1.23.0   | 數值計算            |
| pytest            | >=7.0.0    | 7.4.0      | 測試框架            |
| black             | >=23.0.0   | 23.9.0     | 代碼格式化          |
| flake8            | >=6.0.0    | 6.1.0      | Linter              |
| mypy              | >=1.0.0    | 1.5.0      | 類型檢查            |

注意事項:
1. FlagEmbedding 固定版本（1.3.5）以確保 API 穩定性
2. mem0ai >=1.0.0 確保有 reranker 支持
3. torch 版本由 FlagEmbedding 自動決定
""")


if __name__ == "__main__":
    # Meta-Review 補充: 先檢查 Python 版本和平台
    print("🔍 Meta-Review 補充檢查")
    print()

    python_ok = check_python_version()
    if not python_ok:
        print()
        print("❌ Python 版本不符合要求,請先升級 Python")
        sys.exit(1)

    platform_ok = check_platform_compatibility()
    # 平台警告不阻止繼續

    print()
    print("🔍 依賴版本驗證")
    print()

    success = verify_dependencies()

    if success:
        print()
        print("➡️ 下一步:")
        print("1. 運行 BGE-M3 API 驗證: python scripts/verify_bgem3_api.py")
        print("2. Fork mem0 並驗證 Reranker 接口")
        print("3. 開始 Week 2 開發")
        sys.exit(0)
    else:
        print_installation_guide()
        print_dependency_matrix()
        print()
        print("➡️ 修復依賴問題後重新運行此腳本")
        sys.exit(1)
