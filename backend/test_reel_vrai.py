# test_reel_vrai.py
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_linkedin_sans_hypotheses():
    """Test RÉEL sans hypothèses préconçues"""
    print("🔗 TEST LINKEDIN RÉEL - SANS HYPOTHÈSES")
    print("=" * 50)
    
    try:
        from linkedin_api import Linkedin
        
        # 1. Authentification RÉELLE
        api = Linkedin(
            os.getenv('LINKEDIN_EMAIL'),
            os.getenv('LINKEDIN_PASSWORD')
        )
        print("✅ Authentification LinkedIn réussie!")
        
        # 2. Recherche SANS hypothèse sur le résultat
        print("🔍 Recherche RÉELLE en cours...")
        profiles = api.search_people(
            keywords='CEO OR CTO OR Founder',
            locations=['France'],
            limit=10  # Maximum qu'on demande, mais LinkedIn décide
        )
        
        # 3. Résultat RÉEL (pas d'hypothèse)
        real_count = len(profiles)
        print(f"📊 RÉSULTAT RÉEL: {real_count} profils trouvés")
        
        # 4. Analyse intelligente des résultats
        if real_count == 0:
            print("❌ Aucun profil trouvé - Vérifiez les mots-clés")
            return False
        elif real_count < 5:
            print(f"🟡 Résultat limité: {real_count} profils")
        else:
            print(f"✅ Bon résultat: {real_count} profils")
        
        # 5. Affichage des VRAIS profils
        print(f"\n📋 DÉTAILS DES {real_count} PROFILS RÉELS:")
        for i, profile in enumerate(profiles, 1):
            print(f"\n--- Profil {i}/{real_count} ---")
            print(f"Nom: {profile.get('name', 'N/A')}")
            print(f"Titre: {profile.get('headline', 'N/A')}")
            print(f"Localisation: {profile.get('location', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur LinkedIn: {e}")
        return False

def test_agent_autonome():
    """Test de l'AUTONOMIE réelle de l'agent"""
    print("\n🤖 TEST AUTONOMIE RÉELLE DE L'AGENT")
    print("=" * 50)
    
    try:
        from services.linkedin_agent import LinkedInMitAgent
        
        # Configuration ICP réaliste
        icp_config = {
            'name': 'Test Réel',
            'keywords': ['CEO', 'CTO', 'Startup'],
            'locations': ['Paris', 'Lyon', 'France'],
            'industries': ['Technologie'],
            'limit': 8
        }
        
        # Agent avec VRAIES credentials
        agent = LinkedInMitAgent(
            os.getenv('LINKEDIN_EMAIL'),
            os.getenv('LINKEDIN_PASSWORD')
        )
        
        print("🎯 Surveillance LinkedIn RÉELLE en cours...")
        prospects = agent.monitor_keywords_icp(icp_config)
        
        # Résultat RÉEL (pas d'hypothèse)
        real_prospect_count = len(prospects)
        print(f"📊 RÉSULTAT AUTONOME: {real_prospect_count} prospects traités")
        
        # L'agent est-il VRAIMENT autonome ?
        if real_prospect_count > 0:
            print("✅ AGENT AUTONOME: A trouvé et transformé des prospects!")
            print(f"📧 Exemple: {prospects[0]['personal_info']['full_name']}")
        else:
            print("🟡 AGENT LIMITÉ: Aucun prospect trouvé avec ces critères")
        
        return real_prospect_count > 0
        
    except Exception as e:
        print(f"❌ Erreur agent autonome: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TEST RÉEL SANS HYPOTHÈSES PRÉCONÇUES")
    print("=" * 60)
    
    # Test sans savoir le résultat à l'avance
    linkedin_result = test_linkedin_sans_hypotheses()
    autonomy_result = test_agent_autonome()
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSE RÉELLE DE L'AUTONOMIE")
    print("=" * 60)
    
    if autonomy_result:
        print("✅ VOTRE AGENT EST AUTONOME:")
        print("   - Détection automatique de prospects")
        print("   - Transformation intelligente des données")
        print("   - Adaptation aux résultats réels")
    else:
        print("❌ VOTRE AGENT A BESOIN D'AJUSTEMENTS:")
        print("   - Problème d'authentification LinkedIn")
        print("   - Critères de recherche trop restrictifs")
        print("   - Configuration à revoir")