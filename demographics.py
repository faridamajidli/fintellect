from db_connection import get_db_connection

def fetch_demographics_by_university(university):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT gender, COUNT(*) 
        FROM "User"
        WHERE LOWER(university) = LOWER(%s)
        GROUP BY gender;
    """
    cursor.execute(query, (university,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def fetch_age_distribution_by_university(university):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            CASE
                WHEN age BETWEEN 18 AND 20 THEN '18-20'
                WHEN age BETWEEN 21 AND 23 THEN '21-23'
                WHEN age BETWEEN 24 AND 26 THEN '24-26'
                ELSE '27+'
            END AS age_group,
            COUNT(*)
        FROM "User"
        WHERE LOWER(university) = LOWER(%s)
        GROUP BY age_group;
    """
    cursor.execute(query, (university,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def fetch_demographics_by_city(city):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT gender, COUNT(*) 
        FROM "User"
        WHERE LOWER(city) = LOWER(%s)
        GROUP BY gender;
    """
    cursor.execute(query, (city,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def fetch_age_distribution_by_city(city):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            CASE
                WHEN age BETWEEN 18 AND 20 THEN '18-20'
                WHEN age BETWEEN 21 AND 23 THEN '21-23'
                WHEN age BETWEEN 24 AND 26 THEN '24-26'
                ELSE '27+'
            END AS age_group,
            COUNT(*)
        FROM "User"
        WHERE LOWER(city) = LOWER(%s)
        GROUP BY age_group;
    """
    cursor.execute(query, (city,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
