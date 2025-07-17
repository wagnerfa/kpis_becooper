# app/config.py
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')

DB_USER     = os.getenv('DB_USER',     'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Cooper2022')
DB_HOST     = os.getenv('DB_HOST',     'localhost')
DB_PORT     = os.getenv('DB_PORT',     '3306')
DB_NAME     = os.getenv('DB_NAME',     'kpis_becooper')

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
