import sys
import os

print(f"Python Executable: {sys.executable}")

try:
    import requests
    print("[OK] requests is installed")
except ImportError:
    print("[FAIL] requests is NOT installed")

try:
    from dotenv import load_dotenv
    print("[OK] python-dotenv is installed")
    
    # Try loading .env
    load_dotenv()
    print("Loaded .env")
    
    deepseek = os.getenv('DEEPSEEK_API_KEY')
    if deepseek:
        print(f"[OK] DEEPSEEK_API_KEY found: {deepseek[:5]}...")
    else:
        print("[FAIL] DEEPSEEK_API_KEY NOT found in env")
        
except ImportError:
    print("[FAIL] python-dotenv is NOT installed")
