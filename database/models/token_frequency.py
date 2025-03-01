import sqlite3
from datetime import datetime

def create_token_frequency_table(conn):
    """Creates the token_frequency table in the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_frequency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_token TEXT NOT NULL UNIQUE,
            count INTEGER DEFAULT 1,
            genres TEXT,  -- Stores genres in a comma-separated format, i.e., "rock,pop"
            last_searched DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        conn.rollback()

def insert_token_frequency(conn, search_token, genres):
    """Inserts or updates a token frequency entry."""
    try:
        cursor = conn.cursor()
        
        # Check if the token already exists
        existing_entry = get_token_frequency(conn, search_token)
        if existing_entry:
            # Append new genres (avoiding duplicates) and update the count
            existing_genres = existing_entry[3]  # genres is the 4th column in the result
            if existing_genres:
                all_genres = set(existing_genres.split(',') + genres.split(','))
            else:
                all_genres = set(genres.split(','))  # If no existing genres, use the new genres
            
            updated_genres = ",".join(all_genres)
            
            cursor.execute("""
            UPDATE token_frequency 
            SET count = count + 1, 
                genres = ?, 
                last_searched = CURRENT_TIMESTAMP
            WHERE search_token = ?
            """, (updated_genres, search_token))
        else:
            # If token doesn't exist, insert new record
            cursor.execute("""
            INSERT INTO token_frequency (search_token, count, genres)
            VALUES (?, 1, ?)
            """, (search_token, genres))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting/updating token frequency: {e}")
        conn.rollback()

def get_token_frequency(conn, search_token):
    """Retrieves a token frequency by search token."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM token_frequency WHERE search_token = ?
        """, (search_token,))
        return cursor.fetchone()  # Returns a single row (or None if not found)
    except sqlite3.Error as e:
        print(f"Error fetching token frequency: {e}")
        return None

def update_last_searched(conn, search_token):
    """Updates the last searched timestamp for the token."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE token_frequency 
        SET last_searched = CURRENT_TIMESTAMP
        WHERE search_token = ?
        """, (search_token,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating last searched: {e}")
        conn.rollback()

