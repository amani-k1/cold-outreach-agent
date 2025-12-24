# test_groq.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("🚀 Test Groq (100% gratuit et rapide)...")

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.groq.com/openai/v1"
)

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Dis bonjour en français et présente-toi en 2 phrases"}],
        max_tokens=100
    )
    print("✅ Groq fonctionne parfaitement!")
    print("Réponse:", response.choices[0].message.content)
    print("Modèle:", response.model)
    print("Tokens utilisés:", response.usage.total_tokens)
except Exception as e:
    print(f"❌ Erreur Groq: {e}")