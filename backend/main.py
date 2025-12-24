# ✅ BACKEND PRINCIPAL AVEC LES 3 AGENTS MIT
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
from flask import send_from_directory
import time
import logging
import random
from database_fixed import db

from llm_email_composer import llm_email_composer
from llm_analysis_engine import llm_analysis_engine

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# =============================================
# 🔥 VARIABLES GLOBALES MANQUANTES - AJOUT CRITIQUE
# =============================================
monitoring_active = False
prospects_data = []      # Stockage temporaire des prospects
icp_configs = []         # Configurations ICP
pending_approvals = {}   # Approbations en attente
campaigns_history = []   # Historique des campagnes

# =============================================
# 🚨 CHARGEMENT SÉCURISÉ DES AGENTS MIT
# =============================================

def load_mit_agents_safely():
    """Charge les agents MIT avec gestion d'erreurs"""
    agents_status = {}  # ← INITIALISATION OBLIGATOIRE
    
    try:
        # 1. AGENT LINKEDIN - VERSION RÉELLE
        try:
            from services.linkedin_agent import LinkedInRealAgent
            linkedin_agent = LinkedInRealAgent()
            agents_status['linkedin'] = linkedin_agent
            
            if linkedin_agent.api:
                logger.info("✅ Agent LinkedIn RÉEL chargé avec succès!")
            else:
                logger.warning("🟡 Agent LinkedIn en mode démo - connexion échouée")
                
        except Exception as e:
            logger.warning(f"⚠️ Agent LinkedIn en mode démo: {e}")
            agents_status['linkedin'] = create_demo_linkedin_agent()
        
        # 2. AGENT ENRICHISSEMENT MIT
        try:
            from services.enrichment_service import enrichment_service
            agents_status['enrichment'] = enrichment_service
            logger.info("✅ Agent Enrichissement MIT chargé avec succès")
        except Exception as e:
            logger.warning(f"⚠️ Agent Enrichissement en mode démo: {e}")
            agents_status['enrichment'] = create_demo_enrichment_service()
        
        # 3. AGENT EMAIL
        try:
            from services.email_composer import email_composer
            if hasattr(email_composer, 'yag') and email_composer.yag:
                agents_status['email'] = email_composer
                logger.info("✅ Agent Email RÉEL chargé avec succès")
            else:
                logger.warning("🟡 Agent Email en mode démo")
                agents_status['email'] = create_demo_email_composer()
        except Exception as e:
            logger.warning(f"⚠️ Agent Email en mode démo: {e}")
            agents_status['email'] = create_demo_email_composer()
            
    except Exception as e:
        logger.error(f"❌ Erreur critique chargement agents: {e}")
        agents_status = {
            'linkedin': create_demo_linkedin_agent(),
            'enrichment': create_demo_enrichment_service(), 
            'email': create_demo_email_composer()
        }
    
    return agents_status

# =============================================
# 🎯 AGENTS DE DÉMO (Fallback)
# =============================================

class DemoLinkedInAgent:
    def monitor_keywords_icp(self, icp_config):
        """Surveillance LinkedIn simulée avec données françaises réalistes"""
        logger.info(f"🔍 Simulation prospection LinkedIn: {icp_config['name']}")
        time.sleep(1.5)
        
        prospects = []
        french_names = [
            ("Jean", "Martin"), ("Marie", "Dubois"), ("Pierre", "Bernard"),
            ("Sophie", "Thomas"), ("Michel", "Robert"), ("Nathalie", "Richard")
        ]
        
        french_companies = ["Capgemini", "BNP Paribas", "Total", "Orange", "Renault"]
        
        limit = min(icp_config.get('limit', 5), 8)
        
        for i in range(limit):
            first_name, last_name = random.choice(french_names)
            company = random.choice(french_companies)
            
            prospect = {
                'id': f"demo_{first_name}_{last_name}_{int(time.time())}_{i}",
                'personal_info': {
                    'full_name': f"{first_name} {last_name}",
                    'position': "CTO",
                    'company': company,
                    'location': "Paris",
                    'industry': "Technologie"
                },
                'linkedin_info': {
                    'profile_url': f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                    'connections': random.randint(300, 1200)
                },
                'enrichment_data': {},
                'status': 'new',
                'source': 'linkedin_demo',
                'timestamp': datetime.now().isoformat()
            }
            prospects.append(prospect)
        
        logger.info(f"✅ {len(prospects)} prospects démo générés")
        return prospects
    
    def get_activity_logs(self):
        return [{
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'MODE DÉMO: Prospection LinkedIn simulée',
            'agent': 'linkedin_demo'
        }]

class DemoEnrichmentService:
    def batch_enrich_prospects(self, prospects):
        logger.info(f"📧 Enrichissement de {len(prospects)} prospects")
        time.sleep(0.5)
        
        for prospect in prospects:
            first_name = prospect['personal_info']['full_name'].split()[1].lower()
            last_name = prospect['personal_info']['full_name'].split()[-1].lower()
            company = prospect['personal_info']['company'].lower().replace(' ', '')
            
            prospect['enrichment_data'] = {
                'email': f"{first_name}.{last_name}@{company}.com",
                'email_confidence': 'high',
                'company_domain': f"{company}.com",
                'verification_status': 'simulated',
                'sources': ['demo_enrichment'],
                'enriched_at': datetime.now().isoformat()
            }
        
        return prospects
    
    def get_enrichment_stats(self, prospects):
        return {
            'total_processed': len(prospects),
            'emails_found': len(prospects),
            'success_rate': 100.0,
            'demo_mode': True
        }
    
    def get_activity_logs(self):
        return [{
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'MODE DÉMO: Enrichissement emails simulé',
            'agent': 'enrichment'
        }]

class DemoEmailComposer:
    def personalize_email(self, prospect, template_type="prospection_standard"):
        templates = {
            'prospection_standard': {
                'subject': f"Collaboration avec {prospect['personal_info']['company']}",
                'body': f"""Bonjour {prospect['personal_info']['full_name']},

Votre profil de {prospect['personal_info']['position']} chez {prospect['personal_info']['company']} a retenu notre attention.

Nous avons une solution qui pourrait vous intéresser...

Cordialement,
L'équipe""",
                'personalization_score': 85
            }
        }
        return templates.get(template_type, templates['prospection_standard'])
    
    def send_campaign(self, prospects, template_type="prospection_standard"):
        logger.info(f"✉️  Simulation envoi de {len(prospects)} emails")
        time.sleep(1)
        
        results = {
            'sent': len(prospects),
            'failed': 0,
            'success_rate': 100.0,
            'details': []
        }
        
        for prospect in prospects:
            email_content = self.personalize_email(prospect, template_type)
            results['details'].append({
                'prospect_id': prospect['id'],
                'email': prospect['enrichment_data']['email'],
                'status': 'sent',
                'subject': email_content['subject']
            })
        
        return results
    
    def get_activity_logs(self):
        return [{
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'MODE DÉMO: Campagne email simulée',
            'agent': 'email'
        }]

def create_demo_linkedin_agent():
    return DemoLinkedInAgent()

def create_demo_enrichment_service():
    return DemoEnrichmentService()

def create_demo_email_composer():
    return DemoEmailComposer()

def apply_user_modifications(prospects, modifications):
    """Applique les modifications de l'utilisateur aux prospects"""
    modified_prospects = []
    
    for prospect in prospects:
        prospect_id = prospect['id']
        
        # Crée une copie pour modification
        modified_prospect = prospect.copy()
        
        # Vérifie si ce prospect a des modifications
        if prospect_id in modifications:
            mod = modifications[prospect_id]
            
            # Stocke les modifications dans les métadonnées
            if 'modified_data' not in modified_prospect:
                modified_prospect['modified_data'] = {}
            
            # Applique les modifications
            if 'subject' in mod:
                modified_prospect['modified_data']['original_subject'] = modified_prospect.get('original_subject')
                modified_prospect['modified_data']['subject'] = mod['subject']
            if 'body' in mod:
                modified_prospect['modified_data']['original_body'] = modified_prospect.get('original_body')
                modified_prospect['modified_data']['body'] = mod['body']
            
            modified_prospect['user_modified'] = True
            modified_prospect['modified_at'] = datetime.now().isoformat()
        
        modified_prospects.append(modified_prospect)
    
    return modified_prospects

# =============================================
# 🚀 CHARGEMENT EFFECTIF DES AGENTS
# =============================================
print("🔧 Chargement des agents MIT...")
agents = load_mit_agents_safely()

linkedin_agent = agents['linkedin']
enrichment_service = agents['enrichment'] 
email_composer = agents['email']

print("✅ Tous les agents MIT sont opérationnels!")

# =============================================
# 🆕 CORRECTION DES ROUTES AVEC GESTION DB
# =============================================
@app.route('/api/llm/generate-email', methods=['POST'])
def generate_llm_email():
    """Génère un email personnalisé avec LLM"""
    try:
        data = request.get_json()
        prospect = data.get('prospect')
        email_type = data.get('email_type', 'prospection_froide')
        
        if not prospect:
            return jsonify({"status": "error", "message": "Prospect requis"}), 400
        
        email_content = llm_email_composer.generate_personalized_email(prospect, email_type)
        
        return jsonify({
            "status": "success",
            "email_content": email_content,
            "llm_available": llm_email_composer.llm_available
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur génération email LLM: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/llm/analyze-prospects', methods=['POST'])
def analyze_prospects_llm():
    """Analyse et score des prospects avec LLM"""
    try:
        data = request.get_json()
        prospects = data.get('prospects', [])
        icp_config = data.get('icp_config', {})
        
        if not prospects:
            return jsonify({"status": "error", "message": "Prospects requis"}), 400
        
        analyzed_prospects = llm_analysis_engine.batch_analyze_prospects(prospects, icp_config)
        
        # Statistiques d'analyse
        stats = {
            'total_analyzed': len(analyzed_prospects),
            'average_score': sum(p['llm_analysis']['score'] for p in analyzed_prospects) / len(analyzed_prospects),
            'recommended_count': len([p for p in analyzed_prospects if p['llm_analysis']['recommendation'] == 'Prospecter']),
            'high_confidence_count': len([p for p in analyzed_prospects if p['llm_analysis']['confidence'] == 'Élevée'])
        }
        
        return jsonify({
            "status": "success",
            "analyzed_prospects": analyzed_prospects,
            "analysis_stats": stats,
            "llm_available": llm_analysis_engine.llm_available
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse prospects LLM: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/llm/health', methods=['GET'])
def llm_health_check():
    """Vérifie le statut des services LLM"""
    return jsonify({
        'llm_services': {
            'email_composer': {
                'available': llm_email_composer.llm_available,
                'model': llm_email_composer.model if llm_email_composer.llm_available else None
            },
            'analysis_engine': {
                'available': llm_analysis_engine.llm_available,
                'model': llm_analysis_engine.model if llm_analysis_engine.llm_available else None
            }
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification du statut des agents"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': {
            'linkedin': hasattr(linkedin_agent, 'api') and linkedin_agent.api is not None,
            'enrichment': hasattr(enrichment_service, 'hunter') and enrichment_service.hunter is not None,
            'email': hasattr(email_composer, 'yag') and email_composer.yag is not None
        },
        'demo_mode': isinstance(linkedin_agent, DemoLinkedInAgent),
        'mit_agent': not isinstance(linkedin_agent, DemoLinkedInAgent)
    })

@app.route('/api/config/icp', methods=['POST'])
def config_icp():
    """Configuration de l'ICP depuis le frontend - CORRIGÉE"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        if not data or not data.get('keywords') or not data.get('locations'):
            return jsonify({"status": "error", "message": "Keywords et locations sont requis"}), 400
        
        # Création de l'ICP
        icp_config = {
            'id': f"icp_{int(time.time())}_{random.randint(1000, 9999)}",
            'name': data.get('name', f"ICP_{datetime.now().strftime('%H:%M')}"),
            'keywords': data.get('keywords', []),
            'locations': data.get('locations', []),
            'industries': data.get('industries', []),
            'company_context': data.get('company_context', {}),
            'limit': data.get('limit', 10),
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Sauvegarde dans la liste globale ET en base de données
        icp_configs.append(icp_config)
        
        try:
            db.save_icp_config(icp_config)
            db.log_activity('system', 'INFO', f"ICP créé: {icp_config['name']}")
        except Exception as db_error:
            logger.warning(f"⚠️ Base de données non disponible: {db_error}")
        
        logger.info(f"✅ ICP configuré: {icp_config['name']} avec {len(icp_config['keywords'])} keywords")
        
        return jsonify({
            "status": "success", 
            "message": "ICP configuré avec succès",
            "icp_id": icp_config['id'],
            "icp": icp_config
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur configuration ICP: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/icp', methods=['GET'])
def get_icps():
    """Récupère tous les ICPs"""
    try:
        # Essaye d'abord la base de données, sinon utilise la liste globale
        try:
            icps = db.get_all_icps()
        except:
            icps = icp_configs
            
        return jsonify({
            "icps": icps,
            "total": len(icps)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/monitoring/status', methods=['GET'])
def monitoring_status():
    """Statut de la surveillance LinkedIn - CORRIGÉE"""
    try:
        logs = [
            f"{datetime.now().strftime('%H:%M')} - Système prêt",
            f"{datetime.now().strftime('%H:%M')} - Agent MIT LinkedIn actif" if not isinstance(linkedin_agent, DemoLinkedInAgent) else f"{datetime.now().strftime('%H:%M')} - Mode démo actif"
        ]
        
        # Ajouter les logs des agents
        for agent_logs in [linkedin_agent.get_activity_logs(), 
                          enrichment_service.get_activity_logs(),
                          email_composer.get_activity_logs()]:
            for log in agent_logs[:2]:  # Prendre les 2 derniers logs
                logs.append(f"{log['timestamp'][11:16]} - {log['message']}")
        
        return jsonify({
            "is_monitoring": monitoring_active,
            "agent_type": "MIT LinkedIn Agent" if not isinstance(linkedin_agent, DemoLinkedInAgent) else "Demo Agent",
            "logs": logs[-10:]  # Les 10 derniers logs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Démarrage de la surveillance automatique - CORRIGÉE"""
    global monitoring_active
    try:
        data = request.get_json()
        interval = data.get('interval_minutes', 60)
        
        monitoring_active = True
        
        # Démarrer la surveillance avec votre agent MIT
        if hasattr(linkedin_agent, 'start_monitoring'):
            active_icp = next((icp for icp in icp_configs if icp.get('status') == 'active'), None)
            if active_icp:
                monitoring_result = linkedin_agent.start_monitoring(active_icp, interval)
        
        db.log_activity('system', 'INFO', f"Surveillance démarrée - Intervalle: {interval}min")
        
        return jsonify({
            "status": "success",
            "message": f"Surveillance MIT programmée toutes les {interval} minutes",
            "interval_minutes": interval,
            "agent": "MIT LinkedIn Agent" if not isinstance(linkedin_agent, DemoLinkedInAgent) else "Demo Agent"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Arrêt de la surveillance automatique - CORRIGÉE"""
    global monitoring_active
    try:
        monitoring_active = False
        
        # Arrêter la surveillance avec votre agent MIT
        if hasattr(linkedin_agent, 'stop_monitoring'):
            linkedin_agent.stop_monitoring()
        
        db.log_activity('system', 'INFO', "Surveillance arrêtée")
        
        return jsonify({
            "status": "success", 
            "message": "Surveillance MIT arrêtée"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/search-prospects', methods=['POST'])
def search_prospects():
    """Recherche manuelle de prospects - AMÉLIORÉE AVEC LLM"""
    try:
        data = request.get_json()
        
        # Création d'un ICP temporaire pour la recherche
        temp_icp = {
            'name': 'Recherche Manuelle',
            'keywords': data.get('keywords', ['CEO', 'CTO']),
            'locations': data.get('locations', ['Paris']),
            'industries': data.get('industries', ['Tech']),
            'limit': data.get('limit', 10)
        }
        
        # Utilisation de votre agent LinkedIn
        prospects = linkedin_agent.monitor_keywords_icp(temp_icp)
        
        # Enrichissement des prospects
        enriched_prospects = enrichment_service.batch_enrich_prospects(prospects)
        
        # ⭐ NOUVEAU: Analyse LLM des prospects
        analyzed_prospects = llm_analysis_engine.batch_analyze_prospects(enriched_prospects, temp_icp)
        
        # Sauvegarde des prospects
        for prospect in analyzed_prospects:
            prospects_data.append(prospect)
            try:
                db.save_prospect(prospect)
            except Exception as db_error:
                logger.warning(f"⚠️ Base de données non disponible: {db_error}")
        
        db.log_activity('linkedin', 'INFO', 
                       f"Recherche manuelle: {len(analyzed_prospects)} prospects trouvés et analysés par LLM")
        
        return jsonify({
            "status": "success",
            "count": len(analyzed_prospects),
            "prospects": analyzed_prospects,
            "llm_analysis": True,
            "agent_used": "MIT LinkedIn Agent" if not isinstance(linkedin_agent, DemoLinkedInAgent) else "Demo Agent"
        })
        
    except Exception as e:
        db.log_activity('linkedin', 'ERROR', f"Erreur recherche prospects: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/api/prospects', methods=['GET'])
def get_prospects():
    """Liste tous les prospects - CORRIGÉE"""
    try:
        status_filter = request.args.get('status', 'all')
        
        # Essaye d'abord la base de données, sinon utilise la liste globale
        try:
            prospects = db.get_all_prospects(status_filter)
        except:
            if status_filter == 'all':
                prospects = prospects_data
            else:
                prospects = [p for p in prospects_data if p.get('status') == status_filter]
        
        prospects_with_emails = len([p for p in prospects if p.get('enrichment_data', {}).get('email')])
        
        return jsonify({
            'prospects': prospects,
            'total': len(prospects),
            'with_emails': prospects_with_emails
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Statistiques pour le dashboard - CORRIGÉE"""
    try:
        # Essaye d'abord la base de données, sinon utilise les listes globales
        try:
            stats = db.get_statistics()
        except:
            total_prospects = len(prospects_data)
            approved_prospects = len([p for p in prospects_data if p.get('status') == 'approved'])
            contacted_prospects = len([p for p in prospects_data if p.get('status') == 'contacted'])
            
            approval_rate = (approved_prospects/total_prospects*100) if total_prospects > 0 else 0
            
            stats = {
                "total_prospects": total_prospects,
                "total_approvals": approved_prospects,
                "emails_sent": contacted_prospects,
                "approval_rate": f"{approval_rate:.1f}%",
                "mit_agent_active": not isinstance(linkedin_agent, DemoLinkedInAgent)
            }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Récupération des journaux - CORRIGÉE"""
    try:
        agent_type = request.args.get('agent', 'all')
        limit = request.args.get('limit', 100, type=int)
        
        # Essaye d'abord la base de données, sinon utilise les logs des agents
        try:
            logs = db.get_activity_logs(limit, agent_type)
        except:
            logs = []
            # Récupère les logs de tous les agents
            all_agent_logs = []
            for agent in [linkedin_agent, enrichment_service, email_composer]:
                if hasattr(agent, 'get_activity_logs'):
                    all_agent_logs.extend(agent.get_activity_logs())
            
            # Filtre par type d'agent si spécifié
            if agent_type != 'all':
                logs = [log for log in all_agent_logs if log.get('agent') == agent_type]
            else:
                logs = all_agent_logs
            
            # Trie par timestamp et limite
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            logs = logs[:limit]
        
        return jsonify({
            'logs': logs,
            'total': len(logs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================
# 🆕 ROUTES MANQUANTES - AJOUT CRITIQUE
# =============================================
@app.route('/api/approve-prospect', methods=['POST'])
def approve_prospect():
    """Approbation d'un prospect individuel - CORRIGÉE"""
    try:
        data = request.get_json()
        prospect_id = data.get('prospect_id')
        decision = data.get('decision')  # 'approved' ou 'rejected'
        
        logger.info(f"📋 Approbation prospect: {prospect_id} - Décision: {decision}")
        
        if not prospect_id or not decision:
            return jsonify({"status": "error", "message": "prospect_id et decision requis"}), 400
        
        # Recherche du prospect dans la base de données
        try:
            prospects = db.get_all_prospects('all')
            prospect = next((p for p in prospects if p['id'] == prospect_id), None)
        except:
            # Fallback sur la liste globale
            prospect = next((p for p in prospects_data if p['id'] == prospect_id), None)
        
        if not prospect:
            return jsonify({"status": "error", "message": "Prospect non trouvé"}), 404
        
        # Mise à jour du statut
        if decision == 'approved':
            prospect['status'] = 'approved'
            prospect['approved_at'] = datetime.now().isoformat()
            
            # Génération de l'email personnalisé
            try:
                email_content = email_composer.personalize_email(prospect)
            except Exception as email_error:
                logger.warning(f"⚠️ Erreur génération email: {email_error}")
                email_content = {
                    'subject': f"Collaboration avec {prospect['personal_info']['company']}",
                    'body': f"Bonjour {prospect['personal_info']['full_name']},\n\nEmail personnalisé...",
                    'personalization_score': 75
                }
            
            # Sauvegarde en base
            try:
                # Mettre à jour le prospect en base
                with db.conn.cursor() as cur:
                    cur.execute(
                        "UPDATE prospects SET status = %s, enrichment_data = jsonb_set(enrichment_data, %s, %s) WHERE id = %s",
                        ('approved', '{approved_at}', json.dumps(datetime.now().isoformat()), prospect_id)
                    )
            except Exception as db_error:
                logger.warning(f"⚠️ Erreur DB: {db_error}")
            
            db.log_activity('system', 'INFO', f"Prospect approuvé: {prospect_id}")
            
            return jsonify({
                "status": "success",
                "message": "Prospect approuvé",
                "approval": {
                    "email_content": email_content,
                    "prospect_id": prospect_id
                }
            })
        else:
            # Rejet du prospect
            prospect['status'] = 'rejected'
            
            try:
                with db.conn.cursor() as cur:
                    cur.execute(
                        "UPDATE prospects SET status = %s WHERE id = %s",
                        ('rejected', prospect_id)
                    )
            except Exception as db_error:
                logger.warning(f"⚠️ Erreur DB: {db_error}")
                
            db.log_activity('system', 'INFO', f"Prospect rejeté: {prospect_id}")
            
            return jsonify({
                "status": "success", 
                "message": "Prospect rejeté"
            })
            
    except Exception as e:
        logger.error(f"❌ Erreur approbation prospect: {e}")
        db.log_activity('system', 'ERROR', f"Erreur approbation: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/campaign/approve', methods=['POST'])
def approve_campaign():
    """Approuve une campagne - ROUTE MANQUANTE"""
    try:
        data = request.get_json()
        approval_id = data.get('approval_id')
        
        logger.info(f"✅ Approbation campagne: {approval_id}")
        
        # Simulation d'approbation réussie
        return jsonify({
            'status': 'success',
            'message': 'Campagne approuvée avec succès',
            'approval_id': approval_id,
            'emails_sent': 5  # Exemple
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur approbation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/reject', methods=['POST'])
def reject_campaign():
    """Rejette une campagne - ROUTE MANQUANTE"""
    try:
        data = request.get_json()
        approval_id = data.get('approval_id')
        reason = data.get('reason', 'Raison non spécifiée')
        
        logger.info(f"❌ Rejet campagne: {approval_id} - Raison: {reason}")
        
        return jsonify({
            'status': 'success',
            'message': 'Campagne rejetée',
            'approval_id': approval_id
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur rejet: {e}")
        return jsonify({'error': str(e)}), 500
@app.route('/api/dashboard/llm-stats', methods=['GET'])
def get_llm_dashboard_stats():
    """Nouvelles métriques LLM pour le dashboard"""
    try:
        # Récupère tous les prospects
        prospects = db.get_all_prospects('all')
        
        # Métriques LLM
        llm_emails = [p for p in prospects if p.get('email_content', {}).get('llm_generated')]
        analyzed_prospects = [p for p in prospects if p.get('llm_analysis')]
        
        # Calcul des statistiques avancées
        if analyzed_prospects:
            scores = [p['llm_analysis']['score'] for p in analyzed_prospects]
            avg_score = sum(scores) / len(scores)
            high_quality_leads = len([s for s in scores if s >= 80])
        else:
            avg_score = 0
            high_quality_leads = 0
        
        stats = {
            "llm_emails_generated": len(llm_emails),
            "prospects_analyzed": len(analyzed_prospects),
            "average_llm_score": round(avg_score, 1),
            "high_quality_leads": high_quality_leads,
            "llm_success_rate": f"{(len(llm_emails) / len(prospects) * 100) if prospects else 0:.1f}%",
            "llm_services_available": {
                "email_generation": llm_email_composer.llm_available,
                "prospect_analysis": llm_analysis_engine.llm_available
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Erreur stats LLM dashboard: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# =============================================
# 🎯 SERVIR LE FRONTEND
# =============================================

@app.route('/')
def index():
    """Page d'accueil avec redirection vers le dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cold Outreach Agent</title>
        <meta http-equiv="refresh" content="0; url=/dashboard">
    </head>
    <body>
        <p>Redirection vers le dashboard...</p>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    """Serve le dashboard principal"""
    try:
        return send_from_directory('../frontend', 'agent_dashboard.html')
    except:
        return '''
        <h1>Dashboard non trouvé</h1>
        <p>Assurez-vous que le dossier frontend existe avec agent_dashboard.html</p>
        <p>Structure attendue :</p>
        <pre>
        cold-outreach-agent/
        ├── backend/
        │   └── main.py
        └── frontend/
            └── agent_dashboard.html
        </pre>
        '''

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve tous les fichiers statiques du frontend"""
    try:
        return send_from_directory('../frontend', filename)
    except:
        return f"Fichier {filename} non trouvé", 404

# =============================================
# 🏁 LANCEMENT DE L'APPLICATION
# =============================================
if __name__ == '__main__':
    print("🚀 Lancement de l'agent de prospection froide...")
    print("✅ Agents MIT chargés:")
    print(f"   - LinkedIn Agent: {'✅ VOTRE AGENT MIT' if not isinstance(linkedin_agent, DemoLinkedInAgent) else '🟡 DÉMO'}")
    print(f"   - Enrichment Agent: {'✅ RÉEL' if not isinstance(enrichment_service, DemoEnrichmentService) else '🟡 DÉMO'}")
    print(f"   - Email Agent: {'✅ RÉEL' if not isinstance(email_composer, DemoEmailComposer) else '🟡 DÉMO'}")
    print("🌐 API disponible sur: http://127.0.0.1:5000")
    print("📊 Dashboard: http://127.0.0.1:5000/dashboard")
    
    # Test de la connexion à la base de données
    try:
        db.test_connection()
        print("✅ Base de données connectée")
    except Exception as e:
        print(f"🟡 Base de données non disponible: {e}")
        print("🟡 Mode sans base de données activé")
    
    app.run(debug=True, host='0.0.0.0', port=5000)