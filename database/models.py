import sqlite3
from config.config import DB_CONFIG

def init_db():
    conn = sqlite3.connect(DB_CONFIG["PATH"])
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, 
                  link_id TEXT, 
                  is_active INTEGER,
                  is_admin INTEGER DEFAULT 0)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS activities
                 (id INTEGER PRIMARY KEY, 
                  email TEXT,
                  name TEXT,
                  description TEXT,
                  niveau TEXT,
                  sous_niveau TEXT,
                  frequence TEXT,
                  score INTEGER,
                  date_creation TEXT)''')
    conn.commit()
    conn.close()

def upsert_user(email, link_id):
    conn = sqlite3.connect(DB_CONFIG["PATH"])
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (email, link_id, is_active) VALUES (?, ?, 1)",
              (email, link_id))
    conn.commit()
    conn.close()