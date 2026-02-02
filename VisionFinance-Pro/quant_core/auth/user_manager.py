import sqlite3
import hashlib
import os

class UserManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Creates the users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hashes a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        """Registers a new user. Returns (success, message)."""
        if not username or not password:
            return False, "Kullanıcı adı ve şifre boş olamaz."
        
        password_hash = self.hash_password(password)
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            conn.close()
            return True, "Kayıt başarılı! Şimdi giriş yapabilirsiniz."
        except sqlite3.IntegrityError:
            return False, "Bu kullanıcı adı zaten alınmış."
        except Exception as e:
            return False, f"Hata oluştu: {str(e)}"

    def login(self, username, password):
        """Logs in a user. Returns True if successful."""
        password_hash = self.hash_password(password)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
        user = c.fetchone()
        conn.close()
        
        return user is not None
