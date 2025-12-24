import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def create_database():
    """Crée la base de données si elle n'existe pas"""
    try:
        # Connexion à PostgreSQL (base par défaut)
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database='postgres',
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Créer la base de données
        db_name = os.getenv('DB_NAME', 'cold_outreach')
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Base de données '{db_name}' créée avec succès")
        else:
            print(f"✅ Base de données '{db_name}' existe déjà")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur création base de données: {e}")

if __name__ == '__main__':
    create_database()