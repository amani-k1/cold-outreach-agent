# test_agents.py
import os
import sys
import json
from datetime import datetime

# Ajouter le chemin actuel pour importer vos modules
sys.path.append(os.path.dirname(__file__))

def test_linkedin_agent():
    """Test de l'agent LinkedIn"""
    print("🔍 TEST AGENT LINKEDIN")
    print("=" * 50)
    
    try:
        from services.linkedin_agent import LinkedInMitAgent
        
        # Création de l'agent
        agent = LinkedInMitAgent()
        print("✅ Agent LinkedIn créé")
        
        # Configuration ICP de test
        icp_config = {
            'name': 'Test ICP',
            'keywords': ['CEO', 'CTO', 'Startup'],
            'locations': ['Paris', 'Lyon'],
            'industries': ['Technologie', 'SaaS'],
            'limit': 5
        }
        
        # Test de surveillance
        print("🎯 Surveillance LinkedIn en cours...")
        prospects = agent.monitor_keywords_icp(icp_config)
        
        print(f"✅ {len(prospects)} prospects détectés")
        
        # Affichage des résultats
        for i, prospect in enumerate(prospects, 1):
            print(f"\n--- Prospect {i} ---")
            print(f"Nom: {prospect['personal_info']['full_name']}")
            print(f"Poste: {prospect['personal_info']['position']}")
            print(f"Entreprise: {prospect['personal_info']['company']}")
            print(f"Localisation: {prospect['personal_info']['location']}")
            print(f"Score: {prospect['linkedin_info']['profile_score']}")
            print(f"Email: {prospect['enrichment_data'].get('email', 'Non enrichi')}")
        
        # Test des logs
        logs = agent.get_activity_logs()
        print(f"\n📝 Logs: {logs[0]['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur agent LinkedIn: {e}")
        return False

def test_enrichment_agent():
    """Test de l'agent d'enrichissement"""
    print("\n📧 TEST AGENT ENRICHISSEMENT")
    print("=" * 50)
    
    try:
        from services.enrichment_service import MITEnrichmentService
        
        # Création de l'agent
        agent = MITEnrichmentService()
        print("✅ Agent Enrichissement créé")
        
        # Données de test
        test_prospects = [
            {
                'id': 'test_1',
                'personal_info': {
                    'full_name': 'Jean Dupont',
                    'position': 'CEO',
                    'company': 'Capgemini',
                    'location': 'Paris',
                    'industry': 'Technologie'
                },
                'linkedin_info': {
                    'profile_url': 'https://linkedin.com/in/jean-dupont',
                    'profile_score': 85,
                    'last_activity': 'Récent'
                },
                'enrichment_data': {
                    'email': None,
                    'email_confidence': 'unknown',
                    'company_domain': 'capgemini.com',
                    'sources': [],
                    'detected_at': datetime.now().isoformat()
                },
                'status': 'new',
                'source': 'test',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'test_2', 
                'personal_info': {
                    'full_name': 'Marie Martin',
                    'position': 'CTO',
                    'company': 'BNP Paribas',
                    'location': 'Lyon',
                    'industry': 'Finance'
                },
                'linkedin_info': {
                    'profile_url': 'https://linkedin.com/in/marie-martin',
                    'profile_score': 90,
                    'last_activity': 'Récent'
                },
                'enrichment_data': {
                    'email': None,
                    'email_confidence': 'unknown',
                    'company_domain': 'bnpparibas.com',
                    'sources': [],
                    'detected_at': datetime.now().isoformat()
                },
                'status': 'new',
                'source': 'test',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        print(f"🎯 Enrichissement de {len(test_prospects)} prospects...")
        
        # Test d'enrichissement
        enriched_prospects = agent.batch_enrich_prospects(test_prospects)
        
        # Affichage des résultats
        for i, prospect in enumerate(enriched_prospects, 1):
            print(f"\n--- Prospect enrichi {i} ---")
            print(f"Nom: {prospect['personal_info']['full_name']}")
            print(f"Email: {prospect['enrichment_data']['email']}")
            print(f"Confiance: {prospect['enrichment_data']['email_confidence']}")
            print(f"Méthode: {prospect['enrichment_data']['verification_method']}")
        
        # Test des statistiques
        stats = agent.get_enrichment_stats(enriched_prospects)
        print(f"\n📊 Statistiques: {stats['emails_found']}/{stats['total_processed']} emails trouvés")
        
        # Test des logs
        logs = agent.get_activity_logs()
        print(f"📝 Logs: {logs[0]['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur agent Enrichissement: {e}")
        return False

def test_email_agent():
    """Test de l'agent d'email"""
    print("\n✉️ TEST AGENT EMAIL")
    print("=" * 50)
    
    try:
        from services.email_composer import email_composer
        
        print("✅ Agent Email chargé")
        
        # Données de test
        test_prospect = {
            'id': 'test_email',
            'personal_info': {
                'full_name': 'Pierre Dubois',
                'position': 'Directeur Marketing',
                'company': 'LVMH',
                'location': 'Paris',
                'industry': 'Luxe'
            },
            'enrichment_data': {
                'email': 'pierre.dubois@lvmh.com',
                'email_confidence': 'high'
            }
        }
        
        # Test de personnalisation d'email
        print("🎯 Personnalisation d'email...")
        email_content = email_composer.personalize_email(test_prospect)
        
        print("📧 Email personnalisé:")
        print(f"Sujet: {email_content['subject']}")
        print(f"Corps:\n{email_content['body']}")
        print(f"Score personnalisation: {email_content['personalization_score']}")
        
        # Test d'envoi (mode simulation si Gmail non configuré)
        print("\n🎯 Test d'envoi d'email...")
        results = email_composer.send_campaign([test_prospect])
        
        print(f"📤 Résultats envoi:")
        print(f" - Emails envoyés: {results['sent']}")
        print(f" - Échecs: {results['failed']}")
        print(f" - Taux réussite: {results['success_rate']}%")
        
        # Test des logs
        logs = email_composer.get_activity_logs()
        print(f"📝 Logs: {logs[0]['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur agent Email: {e}")
        return False

def test_surveillance_automatique():
    """Test du système de surveillance complet"""
    print("\n🔄 TEST SURVEILLANCE AUTOMATIQUE COMPLÈTE")
    print("=" * 50)
    
    try:
        from services.linkedin_agent import LinkedInMitAgent
        from services.enrichment_service import MITEnrichmentService
        from services.email_composer import email_composer
        
        print("🎯 Initialisation des 3 agents...")
        
        # Création des agents
        linkedin_agent = LinkedInMitAgent()
        enrichment_agent = MITEnrichmentService()
        
        print("✅ Tous les agents initialisés")
        
        # Configuration ICP
        icp_config = {
            'name': 'Surveillance Test',
            'keywords': ['CEO', 'CTO'],
            'locations': ['Paris'],
            'industries': ['Technologie'],
            'limit': 3
        }
        
        print("🔍 Phase 1: Surveillance LinkedIn...")
        prospects = linkedin_agent.monitor_keywords_icp(icp_config)
        print(f"✅ {len(prospects)} prospects détectés")
        
        print("📧 Phase 2: Enrichissement des emails...")
        enriched_prospects = enrichment_agent.batch_enrich_prospects(prospects)
        
        emails_trouves = len([p for p in enriched_prospects if p['enrichment_data'].get('email')])
        print(f"✅ {emails_trouves}/{len(enriched_prospects)} emails enrichis")
        
        print("✉️ Phase 3: Personnalisation des emails...")
        for prospect in enriched_prospects[:2]:  # Test sur 2 prospects
            email_content = email_composer.personalize_email(prospect)
            print(f"📧 Email pour {prospect['personal_info']['full_name']}: {email_content['subject']}")
        
        print("\n🎉 SURVEILLANCE AUTOMATIQUE TERMINÉE AVEC SUCCÈS!")
        print(f"📊 Résumé: {len(prospects)} prospects → {emails_trouves} emails → Personnalisation OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur surveillance automatique: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS DES AGENTS")
    print("=" * 60)
    
    results = {
        'linkedin': test_linkedin_agent(),
        'enrichment': test_enrichment_agent(), 
        'email': test_email_agent(),
        'surveillance': test_surveillance_automatique()
    }
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for agent, success in results.items():
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{agent.upper():<15} : {status}")
    
    succes_total = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 TOTAL: {succes_total}/{total_tests} tests réussis")
    
    if succes_total == total_tests:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS! Votre système est opérationnel!")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()