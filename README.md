# Cold Outreach Agent

Agent de prospection froide B2B avec backend Flask, surveillance LinkedIn, enrichissement des prospects et génération d’emails personnalisés via LLM, avec un dashboard web.

## Fonctionnalités
- Surveillance LinkedIn par mots‑clés et ICP, avec mode démo si l’agent réel n’est pas disponible (`backend/main.py:36`).
- Enrichissement des prospects (email, domaine, confiance) avec fallback démo (`backend/main.py:143`).
- Génération d’emails personnalisés via LLM (Groq/OpenAI) (`backend/llm_email_composer.py:11`).
- Analyse et scoring des prospects via LLM (`backend/llm_analysis_engine.py:11`).
- Dashboard web pour config ICP, monitoring, stats et logs (`frontend/agent_dashboard.html`).

## Architecture
- `backend/` Flask + services, DB, LLM
- `frontend/` Dashboard HTML/CSS/JS
- `.gitignore` déjà configuré pour ignorer `.env` et `backend/.env`

## Prérequis
- Python 3.11 ou 3.12
- pip
- PostgreSQL (optionnel, le code fonctionne en mode sans DB si la connexion échoue) (`backend/database_fixed.py:16`)
- Clé API Groq/OpenAI si vous voulez activer les LLM

## Installation
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
```

## Configuration
1. Copier `backend/.env.example` vers `backend/.env`
2. Remplir les variables sensibles:
   - `OPENAI_API_KEY`, `OPENAI_MODEL` (`backend/.env.example:12-15`)
   - `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD` (optionnel)
   - `HUNTER_API_KEY`, `GMAIL_EMAIL`, `GMAIL_APP_PASSWORD` (optionnel)
   - Paramètres PostgreSQL si vous les utilisez
3. Ne commitez jamais `backend/.env` (déjà ignoré par `.gitignore`).

## Démarrage
```bash
python backend/main.py
```
- API: `http://127.0.0.1:5000`
- Dashboard: `http://127.0.0.1:5000/dashboard` (`backend/main.py:860-861`, `backend/main.py:824`)

## Endpoints Principaux (références)
- `POST /api/llm/generate-email` (`backend/main.py:285`)
- `POST /api/llm/analyze-prospects` (`backend/main.py:308`)
- `GET  /api/health` (`backend/main.py:357`)
- `POST /api/config/icp` (`backend/main.py:373`)
- `POST /api/monitoring/start` (`backend/main.py:458`)
- `POST /api/monitoring/stop` (`backend/main.py:485`)
- `POST /api/search-prospects` (`backend/main.py:505`)
- `GET  /api/prospects` (`backend/main.py:551`)
- `GET  /api/dashboard-stats` (`backend/main.py:576`)
- `GET  /api/logs` (`backend/main.py:602`)

### Exemples d’utilisation
```bash
# Configurer un ICP
curl -X POST http://localhost:5000/api/config/icp \
 -H "Content-Type: application/json" \
 -d '{"keywords":["CEO","CTO"],"locations":["Paris"],"industries":["Tech"]}'

# Recherche manuelle de prospects
curl -X POST http://localhost:5000/api/search-prospects \
 -H "Content-Type: application/json" \
 -d '{"keywords":["CTO"],"locations":["Paris"]}'
```

## Vérifications & Tests
- Testez votre clé API OpenAI/Groq:
```bash
python backend/test_openai.py
```
- Le projet n’inclut pas de linter configuré; vous pouvez ajouter `ruff` ou `flake8` si besoin.

## Bonnes Pratiques
- Ne commitez jamais vos secrets (`.env` est ignoré, voir `.gitignore`).
- Remplacez les clés d’exemple dans `backend/.env.example` par des placeholders avant de pousser sur GitHub.

## Licence
Choisissez une licence (ex: MIT) selon vos besoins.
