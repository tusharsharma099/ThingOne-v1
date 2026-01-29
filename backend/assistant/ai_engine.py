import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load .env and check if it exists
if not load_dotenv():
    print("WARNING: .env file nahi mili ya load nahi ho payi!")

# 2. Get API Key and Print Status
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: API Key gayab hai! .env mein OPENAI_API_KEY check karein.")
else:
    print(f"SUCCESS: API Key mil gayi hai (Prefix: {api_key[:5]}...)")

try:
    client = OpenAI(api_key=api_key)
    print("SUCCESS: OpenAI Client initialize ho gaya.")
except Exception as e:
    print(f"FATAL: Client setup fail: {e}")

def ask_ai(prompt: str) -> str:
    print(f"\n[DEBUG] Request bheji ja rahi hai... Prompt: {prompt[:20]}...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            timeout=15.0 # 15 seconds max wait
        )
        
        # Ye confirm karega terminal mein
        print(f"[DEBUG] Response receive hui!")
        print(f"[DEBUG] Actual Model Used: {response.model}")
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"[DEBUG] API CALL FAILED: {str(e)}")
        return f"Error: {str(e)}"

# Direct run karke check karne ke liye
if __name__ == "__main__":
    print("--- Starting AI Engine Test ---")
    res = ask_ai("Bhai, kya tum gpt-4o-mini ho?")
    print(f"\nFinal Result: {res}")