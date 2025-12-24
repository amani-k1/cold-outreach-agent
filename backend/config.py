# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Cold Outreach Agent"
    VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    
settings = Settings()