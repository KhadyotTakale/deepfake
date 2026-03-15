import sys
import os

print("Starting debug_startup.py")
try:
    print("Importing main...")
    from main import app
    print("Successfully imported app from main.py")
except Exception as e:
    print(f"FAILED to import main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Attempting to initialize uvicorn server...")
import uvicorn
try:
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8001)
    print("Uvicorn config created.")
    # We won't actually run it here to avoid blocking, 
    # but the import and config creation should be enough to test imports.
except Exception as e:
    print(f"FAILED to configure uvicorn: {e}")
    traceback.print_exc()
    sys.exit(1)

print("Debug startup SUCCESSFUL.")
