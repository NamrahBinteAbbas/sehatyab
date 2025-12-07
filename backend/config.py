import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST')
    SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
    SUPABASE_DB_PORT = 5432
    SUPABASE_DB_NAME = 'postgres'
    SUPABASE_DB_USER = 'postgres.eguqhbvpahuvzasvwpio'
