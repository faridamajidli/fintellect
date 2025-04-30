import pandas as pd
from db_connection import get_db_connection

def fetch_expense_averages(user_id):
    """
    Fetch average expenses for the user's university and city.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        u.university, u.city,
        (SELECT AVG(grocery) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.university = u.university) AS avg_univ_grocery,
        (SELECT AVG(rent) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.university = u.university) AS avg_univ_rent,
        (SELECT AVG(personal) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.university = u.university) AS avg_univ_personal,
        (SELECT AVG(transportation) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.university = u.university) AS avg_univ_transportation,
        (SELECT AVG(misc) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.university = u.university) AS avg_univ_misc,
        
        (SELECT AVG(grocery) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.city = u.city) AS avg_city_grocery,
        (SELECT AVG(rent) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.city = u.city) AS avg_city_rent,
        (SELECT AVG(personal) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.city = u.city) AS avg_city_personal,
        (SELECT AVG(transportation) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.city = u.city) AS avg_city_transportation,
        (SELECT AVG(misc) FROM "Expense" e JOIN "User" u2 ON e.user_id = u2.user_id WHERE u2.city = u.city) AS avg_city_misc
    FROM "User" u
    WHERE u.user_id = %s;
    """

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not result:
        return None

    return {
        "university": result[0],
        "city": result[1],
        "university_avg": result[2:7],  # Grocery, Rent, Personal, Transport, Misc for university
        "city_avg": result[7:12]  # Grocery, Rent, Personal, Transport, Misc for city
    }

def fetch_user_expenses(user_id):
    """
    Fetch the user's personal expenses.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT grocery, rent, personal, transportation, misc 
    FROM "Expense"
    WHERE user_id = %s;
    """

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not result:
        return None

    return list(result)  # Convert tuple to list

def generate_budget_recommendations(user_id):
    """
    Generate AI-based budget recommendations based on university & city averages.
    Returns a dictionary with separate lists for university and city comparisons.
    """
    user_expenses = fetch_user_expenses(user_id)
    averages = fetch_expense_averages(user_id)

    if not user_expenses or not averages:
        return {
            "university": ["No data available for university comparison."],
            "city": ["No data available for city comparison."]
        }

    categories = ["Grocery", "Rent", "Personal", "Transportation", "Miscellaneous"]
    university_recommendations = []
    city_recommendations = []

    for i, category in enumerate(categories):
        user_spending = user_expenses[i]
        avg_university = averages["university_avg"][i]
        avg_city = averages["city_avg"][i]

        # University-based insights
        if user_spending > avg_university:
            university_recommendations.append(
                f"⚠️ You spend {user_spending - avg_university:.2f} more on {category} than the average student at {averages['university']}. Consider adjusting your budget.")
        elif user_spending < avg_university:
            university_recommendations.append(
                f"✅ You spend {avg_university - user_spending:.2f} less on {category} than the average student at {averages['university']}. Good job!")

        # City-based insights
        if user_spending > avg_city:
            city_recommendations.append(
                f"⚠️ Your {category} spending is {user_spending - avg_city:.2f} higher than the average resident in {averages['city']}. Consider optimizing this category.")
        elif user_spending < avg_city:
            city_recommendations.append(
                f"✅ Your {category} spending is {avg_city - user_spending:.2f} lower than the average resident in {averages['city']}. Keep up the good financial habits!")

    return {
        "university": university_recommendations,
        "city": city_recommendations
    }

def fetch_comparison_data(location_type, location_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    if location_type == 'university':
        query = """
        SELECT 
            AVG(grocery) AS avg_grocery,
            AVG(rent) AS avg_rent,
            AVG(personal) AS avg_personal,
            AVG(transportation) AS avg_transportation,
            AVG(misc) AS avg_misc
        FROM "Expense" e
        JOIN "User" u ON e.user_id = u.user_id
        WHERE u.university = %s;
        """
    elif location_type == 'city':
        query = """
        SELECT 
            AVG(grocery) AS avg_grocery,
            AVG(rent) AS avg_rent,
            AVG(personal) AS avg_personal,
            AVG(transportation) AS avg_transportation,
            AVG(misc) AS avg_misc
        FROM "Expense" e
        JOIN "User" u ON e.user_id = u.user_id
        WHERE u.city = %s;
        """
    else:
        return None

    cursor.execute(query, (location_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return {
            "Grocery": round(result[0], 2),
            "Rent": round(result[1], 2),
            "Personal": round(result[2], 2),
            "Transportation": round(result[3], 2),
            "Miscellaneous": round(result[4], 2)
        }
    return None
