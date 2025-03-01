import sqlite3
from datetime import datetime

def create_user_table(conn):
    """Creates the User table in the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_user_id TEXT NOT NULL UNIQUE,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            user_name TEXT NOT NULL,
            last_login DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        conn.rollback()

def insert_user(conn, spotify_user_id, access_token, refresh_token, user_name):
    """Inserts a new user into the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (spotify_user_id, access_token, refresh_token, user_name)
        VALUES (?, ?, ?, ?)
        """, (spotify_user_id, access_token, refresh_token, user_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")
        conn.rollback()

def get_user(conn, spotify_user_id):
    """Retrieves a user by their Spotify user ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM users WHERE spotify_user_id = ?
        """, (spotify_user_id,))
        return cursor.fetchone()  # Return a single result (or None if not found)
    except sqlite3.Error as e:
        print(f"Error fetching user: {e}")
        return None

def update_last_login(conn, spotify_user_id):
    """Updates the last login timestamp for the user."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET last_login = ? WHERE spotify_user_id = ?
        """, (datetime.now(), spotify_user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating last login: {e}")
        conn.rollback()

