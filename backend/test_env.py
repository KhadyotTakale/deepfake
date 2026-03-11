import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: '{url}'")
print(f"KEY: '{key}'")

if not url or not url.startswith("https://"):
    print("INVALID URL DETECTED")
else:
    print("URL LOOKS VALID")
