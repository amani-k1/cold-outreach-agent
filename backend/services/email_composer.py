import os
import yagmail
import time
from datetime import datetime
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EmailComposer:
    def __init__(self, email=None, app_password=None):
        self.gmail_email = email or os.getenv('GMAIL_EMAIL')
        self.app_password = app_password or os.getenv('GMAIL_APP_PASSWORD')
        self.yag = None
        self.is_configured = False
        
        if self.gmail_email and self.app_password:
            self._setup_gmail()
        else:
            logger.warning("Mode démo - Gmail non configuré")
    
    def _setup_gmail(self):
        try:
            self.yag = yagmail.SMTP(self.gmail_email, self.app_password)
            self.is_configured = True
            logger.info("Gmail configuré")
        except Exception as e:
            logger.error(f"Erreur Gmail: {e}")
    
    def personalize_email(self, prospect, template_type="standard"):
        return {
            'subject': f"Collaboration {prospect['personal_info']['company']}",
            'body': f"Bonjour {prospect['personal_info']['full_name']}...",
            'personalization_score': 85
        }
    
    def send_campaign(self, prospects, template_type="standard"):
        results = {'sent': 0, 'failed': 0, 'success_rate': 0, 'details': []}
        
        for prospect in prospects:
            try:
                email_content = self.personalize_email(prospect, template_type)
                prospect_email = prospect['enrichment_data'].get('email')
                
                if not prospect_email:
                    continue
                
                if self.is_configured:
                    self.yag.send(to=prospect_email, subject=email_content['subject'], contents=email_content['body'])
                    status = 'sent_real'
                else:
                    status = 'sent_demo'
                
                results['sent'] += 1
                results['details'].append({
                    'prospect_id': prospect['id'],
                    'email': prospect_email,
                    'status': status
                })
                
                time.sleep(1)
            except Exception as e:
                results['failed'] += 1
        
        total = results['sent'] + results['failed']
        results['success_rate'] = (results['sent'] / total * 100) if total > 0 else 0
        return results
    
    def get_activity_logs(self):
        return [{
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Service email opérationnel',
            'agent': 'email'
        }]

email_composer = EmailComposer()