from db_connection import get_db_connection
from analysis.due_dates import format_due_date

def fetch_user_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT u.user_id, u.name_stud, u.email, u.university, u.city, u.age, u.gender,
           b.monthly_budget, b.target_saving,
           COALESCE(SUM(e.grocery), 0) AS grocery_expense,
           COALESCE(SUM(e.rent), 0) AS rent_expense,
           COALESCE(SUM(e.personal), 0) AS personal_expense,
           COALESCE(SUM(e.transportation), 0) AS transportation_expense,
           COALESCE(SUM(e.misc), 0) AS misc_expense,
           a.tuition_fees_due_date, a.insurance_due_date,
           i.income_amount
    FROM "User" u
    LEFT JOIN "Budget" b ON u.user_id = b.user_id
    LEFT JOIN "Expense" e ON u.user_id = e.user_id
    LEFT JOIN "Academic_Calendar_Event" a ON u.user_id = a.user_id
    LEFT JOIN "Income" i ON u.user_id = i.user_id
    WHERE u.user_id = %s
    GROUP BY u.user_id, b.monthly_budget, b.target_saving, a.tuition_fees_due_date, a.insurance_due_date, i.income_amount;
    """

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        user_id, name_stud, email, university, city, age, gender, monthly_budget, target_saving, \
        grocery_expense, rent_expense, personal_expense, transportation_expense, misc_expense, \
        tuition_due_date, insurance_due_date, income_amount = result

        # Format dates
        tuition_due_date = format_due_date(tuition_due_date)
        insurance_due_date = format_due_date(insurance_due_date)

        return user_id, name_stud, email, university, city, age, gender, monthly_budget, target_saving, \
               grocery_expense, rent_expense, personal_expense, transportation_expense, misc_expense, \
               tuition_due_date, insurance_due_date, income_amount
    else:
        return None