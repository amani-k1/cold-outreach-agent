import os
from openai import OpenAI
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMAnalysisEngine:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'llama-3.1-8b-instant')
        
        if self.openai_api_key:
            self.client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.llm_available = True
            logger.info("✅ Service d'analyse LLM RÉEL configuré (Groq)")
        else:
            self.llm_available = False
            logger.warning("⚠️ Mode démo - API non configurée")
    
    def analyze_prospect_profile(self, prospect, icp_config):
        if not self.llm_available:
            return self._fallback_analysis(prospect)
        
        try:
            prompt = self._build_analysis_prompt(prospect, icp_config)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en qualification de leads B2B. Analyse les profils prospects pour évaluer leur pertinence. Sois concis."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis_response(analysis_text)
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse prospect: {e}")
            return self._fallback_analysis(prospect)
    
    def _build_analysis_prompt(self, prospect, icp_config):
        personal_info = prospect['personal_info']
        
        return f"""
        Analyse ce prospect pour une campagne B2B:

        Prospect: {personal_info['full_name']}
        Poste: {personal_info.get('position', 'Non spécifié')}
        Entreprise: {personal_info.get('company', 'Non spécifiée')}
        Industrie: {personal_info.get('industry', 'Non spécifiée')}

        Notre cible (ICP):
        Mots-clés: {icp_config.get('keywords', [])}
        Industries: {icp_config.get('industries', [])}

        Réponds en français avec ce format:
        Score: [0-100]
        Confiance: [Élevée/Moyenne/Faible]
        Angle: [angle d'approche]
        Recommandation: [Prospecter/Ne pas prospecter]
        """
    
    def _parse_analysis_response(self, analysis_text):
        lines = analysis_text.split('\n')
        analysis = {
            'score': 50,
            'confidence': 'Moyenne',
            'angle': 'Approche standard',
            'risks': 'Aucun risque identifié',
            'recommendation': 'Prospecter',
            'analyzed_at': datetime.now().isoformat()
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('Score:'):
                try:
                    analysis['score'] = int(line.replace('Score:', '').strip())
                except:
                    pass
            elif line.startswith('Confiance:'):
                analysis['confidence'] = line.replace('Confiance:', '').strip()
            elif line.startswith('Angle:'):
                analysis['angle'] = line.replace('Angle:', '').strip()
            elif line.startswith('Risques:'):
                analysis['risks'] = line.replace('Risques:', '').strip()
            elif line.startswith('Recommandation:'):
                analysis['recommendation'] = line.replace('Recommandation:', '').strip()
        
        return analysis
    
    def _fallback_analysis(self, prospect):
        return {
            'score': 60,
            'confidence': 'Moyenne',
            'angle': 'Approche basée sur le poste',
            'risks': 'Données limitées',
            'recommendation': 'Prospecter',
            'analyzed_at': datetime.now().isoformat(),
            'fallback_analysis': True
        }
    
    def batch_analyze_prospects(self, prospects, icp_config):
        analyzed_prospects = []
        for prospect in prospects:
            analysis = self.analyze_prospect_profile(prospect, icp_config)
            prospect['llm_analysis'] = analysis
            analyzed_prospects.append(prospect)
        
        analyzed_prospects.sort(key=lambda x: x['llm_analysis']['score'], reverse=True)
        return analyzed_prospects

llm_analysis_engine = LLMAnalysisEngine()