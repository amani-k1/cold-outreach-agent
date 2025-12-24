import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("🔍 Test nouvelle clé OpenAI (v1.0+)...")
print(f"Clé API présente: {'✅ OUI' if os.getenv('OPENAI_API_KEY') else '❌ NON'}")

if os.getenv('OPENAI_API_KEY'):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Dis 'OK' en français"}],
            max_tokens=10
        )
        print("✅ NOUVELLE CLÉ FONCTIONNE avec OpenAI v1.0+!")
        print("Réponse:", response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Erreur avec nouvelle clé: {e}")
else:
    print("❌ Aucune clé API trouvée")