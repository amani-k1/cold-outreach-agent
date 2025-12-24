import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.connect()
        if self.conn:
            self.create_tables()

    def connect(self):
        """Établit la connexion à PostgreSQL - Version simplifiée"""
        try:
            # Utilisation directe des valeurs pour éviter les problèmes d'encodage
            self.conn = psycopg2.connect(
                host='localhost',
                database='cold_outreach', 
                user='postgres',
                password='password',  # ⚠️ REMPLACEZ PAR VOTRE VRAI MOT DE PASSE
                port='5432'
            )
            self.conn.autocommit = True
            logger.info("✅ Connecté à PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion PostgreSQL: {str(e)}")
            self.conn = None
            return False

    def test_connection(self):
        """Teste la connexion à la base de données"""
        try:
            if self.conn and not self.conn.closed:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Test connexion échoué: {e}")
            return False

    def create_tables(self):
        """Crée les tables si elles n'existent pas"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                # Table des configurations ICP
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS icp_configs (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        keywords JSONB,
                        locations JSONB,
                        industries JSONB,
                        company_context JSONB,
                        limit_count INTEGER,
                        created_at TIMESTAMP,
                        status TEXT
                    )
                """)

                # Table des prospects
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS prospects (
                        id TEXT PRIMARY KEY,
                        personal_info JSONB,
                        linkedin_info JSONB,
                        enrichment_data JSONB,
                        status TEXT,
                        source TEXT,
                        timestamp TIMESTAMP,
                        icp_id TEXT
                    )
                """)

                # Table des logs d'activité
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        level TEXT,
                        message TEXT,
                        agent TEXT
                    )
                """)

                # Table des campagnes en attente d'approbation
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pending_approvals (
                        approval_id TEXT PRIMARY KEY,
                        prospects JSONB,
                        template_type TEXT,
                        previews JSONB,
                        created_at TIMESTAMP,
                        status TEXT
                    )
                """)

                # Table des campagnes envoyées
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        id TEXT PRIMARY KEY,
                        approval_id TEXT,
                        template_type TEXT,
                        prospects_count INTEGER,
                        results JSONB,
                        sent_at TIMESTAMP
                    )
                """)

                logger.info("✅ Tables PostgreSQL créées avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur création tables: {e}")

    def save_icp_config(self, icp_config):
        """Sauvegarde une configuration ICP"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO icp_configs (id, name, keywords, locations, industries, company_context, limit_count, created_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        keywords = EXCLUDED.keywords,
                        locations = EXCLUDED.locations,
                        industries = EXCLUDED.industries,
                        company_context = EXCLUDED.company_context,
                        limit_count = EXCLUDED.limit_count,
                        status = EXCLUDED.status
                """, (
                    icp_config['id'],
                    icp_config['name'],
                    json.dumps(icp_config.get('keywords', [])),
                    json.dumps(icp_config.get('locations', [])),
                    json.dumps(icp_config.get('industries', [])),
                    json.dumps(icp_config.get('company_context', {})),
                    icp_config.get('limit', 10),
                    icp_config.get('created_at'),
                    icp_config.get('status', 'active')
                ))
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde ICP: {e}")

    def get_icp_by_id(self, icp_id):
        """Récupère un ICP par son ID"""
        if not self.conn:
            return None

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM icp_configs WHERE id = %s", (icp_id,))
                result = cur.fetchone()
                if result:
                    icp = dict(result)
                    # Convertir les champs JSON
                    icp['keywords'] = json.loads(icp['keywords']) if icp['keywords'] else []
                    icp['locations'] = json.loads(icp['locations']) if icp['locations'] else []
                    icp['industries'] = json.loads(icp['industries']) if icp['industries'] else []
                    icp['company_context'] = json.loads(icp['company_context']) if icp['company_context'] else {}
                    return icp
                return None
        except Exception as e:
            logger.error(f"❌ Erreur récupération ICP: {e}")
            return None

    def get_all_icps(self):
        """Récupère toutes les configurations ICP"""
        if not self.conn:
            return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM icp_configs ORDER BY created_at DESC")
                rows = cur.fetchall()
                icps = []
                for row in rows:
                    icp = dict(row)
                    icp['keywords'] = json.loads(icp['keywords']) if icp['keywords'] else []
                    icp['locations'] = json.loads(icp['locations']) if icp['locations'] else []
                    icp['industries'] = json.loads(icp['industries']) if icp['industries'] else []
                    icp['company_context'] = json.loads(icp['company_context']) if icp['company_context'] else {}
                    icps.append(icp)
                return icps
        except Exception as e:
            logger.error(f"❌ Erreur récupération ICPs: {e}")
            return []

    def save_prospect(self, prospect):
        """Sauvegarde un prospect"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO prospects (id, personal_info, linkedin_info, enrichment_data, status, source, timestamp, icp_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        personal_info = EXCLUDED.personal_info,
                        linkedin_info = EXCLUDED.linkedin_info,
                        enrichment_data = EXCLUDED.enrichment_data,
                        status = EXCLUDED.status,
                        source = EXCLUDED.source,
                        icp_id = EXCLUDED.icp_id
                """, (
                    prospect['id'],
                    json.dumps(prospect.get('personal_info', {})),
                    json.dumps(prospect.get('linkedin_info', {})),
                    json.dumps(prospect.get('enrichment_data', {})),
                    prospect.get('status', 'new'),
                    prospect.get('source', ''),
                    prospect.get('timestamp'),
                    prospect.get('icp_id')
                ))
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde prospect: {e}")

    def get_all_prospects(self, status_filter='all'):
        """Récupère tous les prospects"""
        if not self.conn:
            return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if status_filter == 'all':
                    cur.execute("SELECT * FROM prospects ORDER BY timestamp DESC")
                else:
                    cur.execute("SELECT * FROM prospects WHERE status = %s ORDER BY timestamp DESC", (status_filter,))

                rows = cur.fetchall()
                prospects = []
                for row in rows:
                    prospect = dict(row)
                    # Convertir les champs JSON
                    prospect['personal_info'] = json.loads(prospect['personal_info']) if prospect['personal_info'] else {}
                    prospect['linkedin_info'] = json.loads(prospect['linkedin_info']) if prospect['linkedin_info'] else {}
                    prospect['enrichment_data'] = json.loads(prospect['enrichment_data']) if prospect['enrichment_data'] else {}
                    prospects.append(prospect)
                return prospects
        except Exception as e:
            logger.error(f"❌ Erreur récupération prospects: {e}")
            return []

    def update_prospect_status(self, prospect_id, status, contacted_at=None):
        """Met à jour le statut d'un prospect"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                if contacted_at:
                    # Mettre à jour le statut et ajouter contacted_at dans enrichment_data
                    cur.execute("""
                        UPDATE prospects 
                        SET status = %s, enrichment_data = jsonb_set(
                            COALESCE(enrichment_data, '{}'::jsonb),
                            '{contacted_at}', 
                            %s::jsonb,
                            true
                        )
                        WHERE id = %s
                    """, (status, json.dumps(contacted_at), prospect_id))
                else:
                    cur.execute("UPDATE prospects SET status = %s WHERE id = %s", (status, prospect_id))
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour prospect: {e}")

    def log_activity(self, agent, level, message):
        """Log une activité"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO activity_logs (timestamp, level, message, agent)
                    VALUES (%s, %s, %s, %s)
                """, (datetime.now().isoformat(), level, message, agent))
        except Exception as e:
            logger.error(f"❌ Erreur log activité: {e}")

    def get_activity_logs(self, limit=100, agent_type='all'):
        """Récupère les logs d'activité"""
        if not self.conn:
            return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if agent_type == 'all':
                    cur.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
                else:
                    cur.execute("SELECT * FROM activity_logs WHERE agent = %s ORDER BY timestamp DESC LIMIT %s", (agent_type, limit))

                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ Erreur récupération logs: {e}")
            return []

    def save_pending_approval(self, approval_data):
        """Sauvegarde une approbation en attente"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pending_approvals (approval_id, prospects, template_type, previews, created_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (approval_id) DO UPDATE SET
                        prospects = EXCLUDED.prospects,
                        template_type = EXCLUDED.template_type,
                        previews = EXCLUDED.previews,
                        status = EXCLUDED.status
                """, (
                    approval_data['approval_id'],
                    json.dumps(approval_data.get('prospects', [])),
                    approval_data.get('template_type'),
                    json.dumps(approval_data.get('previews', [])),
                    approval_data.get('created_at'),
                    approval_data.get('status', 'pending')
                ))
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde approbation: {e}")

    def get_pending_approval(self, approval_id):
        """Récupère une approbation en attente"""
        if not self.conn:
            return None

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM pending_approvals WHERE approval_id = %s", (approval_id,))
                row = cur.fetchone()
                if row:
                    approval = dict(row)
                    approval['prospects'] = json.loads(approval['prospects']) if approval['prospects'] else []
                    approval['previews'] = json.loads(approval['previews']) if approval['previews'] else []
                    return approval
                return None
        except Exception as e:
            logger.error(f"❌ Erreur récupération approbation: {e}")
            return None

    def delete_pending_approval(self, approval_id):
        """Supprime une approbation en attente"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM pending_approvals WHERE approval_id = %s", (approval_id,))
        except Exception as e:
            logger.error(f"❌ Erreur suppression approbation: {e}")

    def save_campaign(self, campaign_record):
        """Sauvegarde une campagne envoyée"""
        if not self.conn:
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO campaigns (id, approval_id, template_type, prospects_count, results, sent_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    campaign_record['id'],
                    campaign_record.get('approval_id'),
                    campaign_record.get('template_type'),
                    campaign_record.get('prospects_count'),
                    json.dumps(campaign_record.get('results', {})),
                    datetime.now().isoformat()
                ))
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde campagne: {e}")

    def get_statistics(self):
        """Récupère les statistiques"""
        if not self.conn:
            return {}

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Total prospects
                cur.execute("SELECT COUNT(*) as total FROM prospects")
                total_prospects = cur.fetchone()['total']

                # Prospects approuvés
                cur.execute("SELECT COUNT(*) as approved FROM prospects WHERE status = 'approved'")
                approved_prospects = cur.fetchone()['approved']

                # Prospects contactés
                cur.execute("SELECT COUNT(*) as contacted FROM prospects WHERE status = 'contacted'")
                contacted_prospects = cur.fetchone()['contacted']

                # Prospects avec emails
                cur.execute("""
                    SELECT COUNT(*) as with_emails 
                    FROM prospects 
                    WHERE enrichment_data->>'email' IS NOT NULL 
                    AND enrichment_data->>'email' != ''
                """)
                with_emails = cur.fetchone()['with_emails']

                # Taux d'approbation
                approval_rate = (approved_prospects / total_prospects * 100) if total_prospects > 0 else 0

                return {
                    "total_prospects": total_prospects,
                    "total_approvals": approved_prospects,
                    "emails_sent": contacted_prospects,
                    "with_emails": with_emails,
                    "approval_rate": f"{approval_rate:.1f}%"
                }
        except Exception as e:
            logger.error(f"❌ Erreur récupération statistiques: {e}")
            return {}

# Instance globale de la base de données
db = DatabaseManager()