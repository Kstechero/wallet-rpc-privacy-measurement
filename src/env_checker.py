import os

def check_m3_environment():
    print("=" * 50)
    print("M3 Environment Checker (Role 2 Contribution)")
    print("This script ONLY checks file existence. No modification.")
    print("=" * 50)

    check_items = [
        "src/runner.py",
        "src/rpc_client.py",
        "src/summarize.py",
        "src/batch_run.py",
        "configs/m3",
        "README.md"
    ]

    all_good = True
    for item in check_items:
        if os.path.exists(item):
            print(f"✅ OK: {item}")
        else:
            print(f"❌ MISSING: {item}")
            all_good = False

    print("=" * 50)
    if all_good:
        print("Result: M3 environment appears ready.")
    else:
        print("Result: Some files missing.")
    print("=" * 50)

if __name__ == "__main__":
    check_m3_environment()