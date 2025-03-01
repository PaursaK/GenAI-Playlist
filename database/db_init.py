import sqlite3
from database.models.user import create_user_table
from database.models.token_frequency import create_token_frequency_table

def init_db(db_name='spotify_gen_ai.db'):
    """Initialize the SQLite database and create necessary tables."""
    conn = sqlite3.connect(db_name)
    create_user_table(conn)
    create_token_frequency_table(conn)
    conn.close()
    print("Database and tables created successfully!")

if __name__ == "__main__":
    init_db()