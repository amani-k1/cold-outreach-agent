# test_deepseek.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("🧪 Test DeepSeek (gratuit)...")

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.deepseek.com"
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Dis bonjour en français et présente-toi en 2 phrases"}],
        max_tokens=100
    )
    print("✅ DeepSeek fonctionne parfaitement!")
    print("Réponse:", response.choices[0].message.content)
    print("Tokens utilisés:", response.usage.total_tokens)
except Exception as e:
    print(f"❌ Erreur: {e}")