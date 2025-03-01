import sqlite3
from database.models.user import *
from database.models.token_frequency import *

def get_db_connection(db_name='spotify_gen_ai.db'):
    """Establishes a database connection."""
    conn = sqlite3.connect(db_name)
    return conn

def add_user(spotify_user_id, access_token, refresh_token, user_name):
    """Add a new user to the database."""
    conn = get_db_connection()
    insert_user(conn, spotify_user_id, access_token, refresh_token, user_name)
    conn.close()


def fetch_user(spotify_user_id):
    """Fetch a user by Spotify user ID."""
    conn = get_db_connection()
    user = get_user(conn, spotify_user_id)
    conn.close()
    return user

def update_token_frequency_with_genres(tokens, genres):
    """Update or insert tokens with the associated genres (3 genres)."""
    try:
        conn = get_db_connection()

        for token in tokens:
            # Check if the token already exists in the database
            existing_token = fetch_token_frequency(token)

            if existing_token:
                # Token exists, update the count and append the new genres (if not already present)
                current_genres = existing_token[3]  # The existing genres in the database
                genre_list = current_genres.split(',')  # Convert current genres to a list
                # Ensure we are adding only unique genres
                updated_genres = list(set(genre_list + genres))  # Combine and remove duplicates
                updated_genres_str = ",".join(updated_genres)  # Convert back to a comma-separated string

                # Update the token's count and genres
                insert_token_frequency(conn, token, updated_genres_str)
            else:
                # Token does not exist, insert a new entry with the count and genres
                genres_str = ",".join(genres)  # Convert the list to a comma-separated string
                insert_token_frequency(conn, token, genres_str)
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Error updating token frequency with genres: {e}")



def fetch_token_frequency(search_token):
    """Fetch a token's frequency."""
    try:
        conn = get_db_connection()
        token_data = get_token_frequency(conn, search_token)
        conn.close()
        return token_data
    except sqlite3.Error as e:
        print(f"Error fetching token frequency: {e}")
        return None

def fetch_trending_tokens(limit=20):
    """Fetch top trending tokens based on frequency"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query the database to get the top tokens ordered by frequency
        cursor.execute("""
        SELECT search_token, count, genres, last_searched
        FROM token_frequency
        ORDER BY count DESC
        LIMIT ?
        """, (limit,))
        
        # Fetch all the results
        trending_tokens = cursor.fetchall()
        
        # Return a list of token data (for display in your app)
        return [{
            "search_token": token[0],
            "count": token[1],
            "genres": token[2],
            "last_searched": token[3]
        } for token in trending_tokens]
    
    except Exception as e:
        print(f"Error fetching trending tokens: {e}")
        return []

def print_all_users():
    """Print all users in the users table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    print("All Users:", users)

def print_all_token_frequencies():
    """Print all token frequencies in the token_frequency table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM token_frequency")
    tokens = cursor.fetchall()
    conn.close()
    print("All Token Frequencies:", tokens)

def drop_tables(db_name='spotify_gen_ai.db'):
    """Drops all tables in the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("DROP TABLE IF EXISTS token_frequency;")
        conn.commit()
        print("All tables dropped successfully!")
    except sqlite3.Error as e:
        print(f"Error dropping tables: {e}")
    finally:
        conn.close()
