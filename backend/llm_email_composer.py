import os
from openai import OpenAI
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMEmailComposer:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'llama-3.1-8b-instant')
        
        if self.openai_api_key:
            self.client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.llm_available = True
            logger.info("✅ Service LLM RÉEL configuré (Groq)")
        else:
            self.llm_available = False
            logger.warning("⚠️ Mode démo - API non configurée")
    
    def generate_personalized_email(self, prospect, email_type="prospection_froide"):
        if not self.llm_available:
            return self._fallback_email(prospect)
        
        try:
            prompt = self._build_email_prompt(prospect, email_type)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un commercial expert français, spécialiste dans la prospection B2B. Tu écris des emails percutants, personnalisés et respectueux. Sois concis et direct."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            email_content = response.choices[0].message.content
            return self._parse_llm_response(email_content, prospect)
            
        except Exception as e:
            logger.error(f"❌ Erreur génération email: {e}")
            return self._fallback_email(prospect)
    
    def _build_email_prompt(self, prospect, email_type):
        personal_info = prospect['personal_info']
        
        prompt = f"""
        Écris un email de prospection professionnel en français avec ces informations:

        Destinataire: {personal_info['full_name']}
        Poste: {personal_info.get('position', 'Non spécifié')}
        Entreprise: {personal_info.get('company', 'Non spécifiée')}
        Industrie: {personal_info.get('industry', 'Non spécifiée')}

        Contraintes:
        - 80-120 mots maximum
        - Ton professionnel mais chaleureux
        - Accroche personnalisée
        - Proposition de valeur concise
        - Appel à action clair

        Format de réponse:
        Sujet: [sujet]
        Corps: [email]
        """
        
        return prompt
    
    def _parse_llm_response(self, email_content, prospect):
        lines = email_content.split('\n')
        subject = ""
        body = ""
        
        for line in lines:
            if line.startswith('Sujet:'):
                subject = line.replace('Sujet:', '').strip()
            elif line.startswith('Corps:'):
                body = line.replace('Corps:', '').strip()
            elif line and not subject and len(line) < 100:
                subject = line
            elif line and not body:
                body = line
            elif line:
                body += "\n" + line
        
        # Nettoyer le body
        body = body.strip()
        
        return {
            'subject': subject or f"Collaboration {prospect['personal_info']['company']}",
            'body': body or self._fallback_email(prospect)['body'],
            'personalization_score': 90,
            'llm_generated': True,
            'generated_at': datetime.now().isoformat(),
            'model_used': self.model
        }
    
    def _fallback_email(self, prospect):
        return {
            'subject': f"Collaboration {prospect['personal_info']['company']}",
            'body': f"""Bonjour {prospect['personal_info']['full_name']},

Votre profil de {prospect['personal_info']['position']} chez {prospect['personal_info']['company']} a retenu mon attention.

Je souhaiterais échanger sur une collaboration potentielle.

Disponible pour un call de 15 minutes cette semaine ?

Cordialement,""",
            'personalization_score': 75,
            'llm_generated': False
        }

llm_email_composer = LLMEmailComposer()