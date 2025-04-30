import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="fintellect",  # Use your database name
        user="postgres",
        password="Mastan4ik"
    )
    return conn