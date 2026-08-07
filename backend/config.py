import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "ppa-super-secret-key"
    JWT_SECRET_KEY = "ppa-jwt-super-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "ppa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    # Cache config — falls back to SimpleCache if Redis is unavailable
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 120
    
    # SMTP config for reminders and monthly reports
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "25f2001780@ds.study.iitm.ac.in")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "dkelnlzxtdhrsozv")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "25f2001780@ds.study.iitm.ac.in")
    
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "25f2001780@ds.study.iitm.ac.in")
