import sys
import os
import traceback

# Add current directory to path (simulating running from backend)
sys.path.append(os.getcwd())

modules_to_test = [
    "app.routes.analytics",
    "app.routes.pattern_recognition",
    "app.routes.katooling_workflow"
]

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

for module_name in modules_to_test:
    print(f"\n--- Testing import: {module_name} ---")
    try:
        __import__(module_name, fromlist=["router"])
        print(f"✅ Success: {module_name}")
    except Exception:
        print(f"❌ Failed: {module_name}")
        traceback.print_exc()
