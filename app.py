from flask import Flask, render_template, request, redirect, url_for
from flask import render_template, request, redirect, url_for, session
from db_connection import get_db_connection
from fetch_data import fetch_user_data
from ai_budget_recommendations import generate_budget_recommendations, fetch_comparison_data
from analysis.expense_analysis import generate_expense_charts
from analysis.user_profile import calculate_savings
from analysis.due_dates import check_due_status
from ai_chatbot import generate_financial_plan
from demographics import (
    fetch_demographics_by_university,
    fetch_age_distribution_by_university,
    fetch_demographics_by_city,
    fetch_age_distribution_by_city
)
from financial_planner import generate_financial_plan_prompt
import os

app = Flask(__name__)
app.secret_key = 'admin'

@app.route('/signup/step1', methods=['GET', 'POST'])
def signup_step1():
    if request.method == 'POST':
        # Store basic user info in session
        session['name_stud'] = request.form['name_stud']
        session['email'] = request.form['email']
        session['gender'] = request.form['gender']
        session['age'] = request.form['age']
        session['university'] = request.form['university']
        session['city'] = request.form['city']
        return redirect(url_for('signup_step2'))
    return render_template('signup_step1.html')

@app.route('/signup/step2', methods=['GET', 'POST'])
def signup_step2():
    if request.method == 'POST':
        session['monthly_budget'] = request.form['monthly_budget']
        session['target_saving'] = request.form['target_saving']
        session['wage_per_hour'] = request.form['wage_per_hour']
        return redirect(url_for('signup_step3'))
    return render_template('signup_step2.html')

@app.route('/signup/step3', methods=['GET', 'POST'])
def signup_step3():
    if request.method == 'POST':
        session['rent'] = request.form['rent']
        session['grocery'] = request.form['grocery']
        session['transportation'] = request.form['transportation']
        session['personal'] = request.form['personal']
        session['misc'] = request.form['misc']
        return redirect(url_for('signup_step4'))
    return render_template('signup_step3.html')

@app.route('/signup/step4', methods=['GET', 'POST'])
def signup_step4():
    if request.method == 'POST':
        session['ef_knowledge'] = request.form['ef_knowledge']
        session['tuition_fees_due_date'] = request.form['tuition_fees_due_date']
        session['insurance_due_date'] = request.form['insurance_due_date']
        
        # Once all steps are complete, insert into DB
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists (optional but recommended)
        cursor.execute('SELECT user_id FROM "User" WHERE email = %s;', (session['email'],))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('error.html', message="A user with this email already exists. Please log in.")

        # Insert into "User" table (auto-assigns unique student ID)
        cursor.execute("""
            INSERT INTO "User" (name_stud, email, gender, age, university, city)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING user_id;
        """, (session['name_stud'], session['email'], session['gender'],
              session['age'], session['university'], session['city']))
        new_user_id = cursor.fetchone()[0]

        # Insert into "Budget" table
        cursor.execute("""
            INSERT INTO "Budget" (user_id, monthly_budget, target_saving)
            VALUES (%s, %s, %s);
        """, (new_user_id, session['monthly_budget'], session['target_saving']))

        # Insert into "Income" table (calculating monthly income as wage_per_hour * 20 * 4)
        monthly_income = float(session['wage_per_hour']) * 20 * 4
        cursor.execute("""
            INSERT INTO "Income" (user_id, income_amount)
            VALUES (%s, %s);
        """, (new_user_id, monthly_income))

        # Insert into "Expense" table
        cursor.execute("""
            INSERT INTO "Expense" (user_id, rent, grocery, transportation, personal, misc)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (new_user_id, session['rent'], session['grocery'], session['transportation'],
              session['personal'], session['misc']))

        # Insert into "Emergency_Fund" table
        cursor.execute("""
            INSERT INTO "Emergency_Fund" (user_id, ef_knowledge)
            VALUES (%s, %s);
        """, (new_user_id, session['ef_knowledge']))

        # Insert into "Academic_Calendar_Event" table
        cursor.execute("""
            INSERT INTO "Academic_Calendar_Event" (user_id, tuition_fees_due_date, insurance_due_date)
            VALUES (%s, %s, %s);
        """, (new_user_id, session['tuition_fees_due_date'], session['insurance_due_date']))

        conn.commit()
        cursor.close()
        conn.close()

        # Clear the session for sign-up data
        session.clear()

        # Pass the new user id to the success page
        return render_template('success.html', 
                               message="Sign-up successful! Please remember your Student ID for logging in.",
                               user_id=new_user_id)
    
    return render_template('signup_step4.html')

# Route for the About page (landing page)
@app.route('/')
def about():
    return render_template('about.html')

# Route for Login page (GET displays the form; POST processes login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id_to_fetch = request.form['user_id']
        result = fetch_user_data(user_id_to_fetch)
        if result:
            # Unpack the result
            (user_id, name_stud, email, university, city, age, gender,
             monthly_budget, target_saving, grocery_expense, rent_expense,
             personal_expense, transportation_expense, misc_expense,
             tuition_due_date, insurance_due_date, income_amount) = result

            total_expense = (grocery_expense + rent_expense + personal_expense +
                             transportation_expense + misc_expense)
            total_saving = calculate_savings(income_amount, total_expense)

            bar_chart_html, pie_chart_html = generate_expense_charts(
                grocery_expense, rent_expense, personal_expense, transportation_expense, misc_expense
            )

            tuition_due_status = check_due_status(tuition_due_date)
            insurance_due_status = check_due_status(insurance_due_date)

            recommendations_split = generate_budget_recommendations(user_id)
            university_recommendations = recommendations_split["university"]
            city_recommendations = recommendations_split["city"]

            financial_plan = generate_financial_plan(user_id)

            # Render the unified dashboard with all personalized data
            return render_template(
                'dashboard.html',
                user_id=user_id,
                name_stud=name_stud,
                email=email,
                university=university,
                city=city,
                age=age,
                gender=gender,
                monthly_budget=monthly_budget,
                income_amount=income_amount,
                target_saving=target_saving,
                total_expense=total_expense,
                total_saving=total_saving,
                tuition_due_date=tuition_due_date,
                insurance_due_date=insurance_due_date,
                tuition_due_status=tuition_due_status,
                insurance_due_status=insurance_due_status,
                bar_chart_html=bar_chart_html,
                pie_chart_html=pie_chart_html,
                university_recommendations=university_recommendations,
                city_recommendations=city_recommendations,
                financial_plan=financial_plan
            )
        else:
            return render_template('error.html', message="User not found. Please enter a valid user ID.")
    return render_template('login.html')

# The following routes remain unchanged

@app.route('/profile/<int:user_id>')
def profile(user_id):
    result = fetch_user_data(user_id)
    if result:
        (user_id, name_stud, email, university, city, age, gender,
         monthly_budget, target_saving, grocery_expense, rent_expense,
         personal_expense, transportation_expense, misc_expense,
         tuition_due_date, insurance_due_date, income_amount) = result

        total_expense = (grocery_expense + rent_expense + personal_expense +
                         transportation_expense + misc_expense)
        total_saving = calculate_savings(income_amount, total_expense)

        return render_template(
            "user_profile.html",
            user_id=user_id,
            name_stud=name_stud,
            email=email,
            university=university,
            city=city,
            age=age,
            gender=gender,
            monthly_budget=monthly_budget,
            income_amount=income_amount,
            target_saving=target_saving,
            total_expense=total_expense,
            total_saving=total_saving
        )
    else:
        return render_template('error.html', message="User not found.")
    
@app.route('/comparison/<int:user_id>/<string:location_type>/<string:location_name>')
def comparison(user_id, location_type, location_name):
    # Validate location_type
    if location_type.lower() not in ['university', 'city']:
        return render_template('error.html', message="Invalid comparison type.")
    
    # Retrieve expense comparison data
    comparison_data = fetch_comparison_data(location_type, location_name)
    if not comparison_data:
        return render_template('error.html', message="No comparison data available.")
    
    # Retrieve user data to get university and city
    result = fetch_user_data(user_id)
    if not result:
        return render_template('error.html', message="User not found.")
    
    # Unpack user data (ensure university and city are available)
    # Note: Adjust the unpacking order if necessary.
    _, _, _, university, city, _, _, _, _, user_grocery, user_rent, user_personal, user_transportation, user_misc, _, _, _ = result

    # Build expense comparison table
    user_expenses = {
        "Grocery": user_grocery,
        "Rent": user_rent,
        "Personal": user_personal,
        "Transportation": user_transportation,
        "Miscellaneous": user_misc
    }
    categories = ["Grocery", "Rent", "Personal", "Transportation", "Miscellaneous"]
    comparison_table = {}
    for category in categories:
        avg = comparison_data.get(category)
        user_val = user_expenses.get(category)
        comparison_table[category] = {"average": avg, "user": user_val}
    
    # Retrieve demographic data depending on location_type
    if location_type.lower() == 'university':
        demographics_gender = fetch_demographics_by_university(university)
        demographics_age = fetch_age_distribution_by_university(university)
    else:
        demographics_gender = fetch_demographics_by_city(city)
        demographics_age = fetch_age_distribution_by_city(city)
    
    gender_labels = [row[0] for row in demographics_gender]
    gender_values = [row[1] for row in demographics_gender]
    age_labels = [row[0] for row in demographics_age]
    age_values = [row[1] for row in demographics_age]
    
    return render_template(
        'comparison.html',
        user_id=user_id,
        location_type=location_type,
        location_name=location_name,
        data=comparison_table,
        gender_labels=gender_labels,
        gender_values=gender_values,
        age_labels=age_labels,
        age_values=age_values
    )

@app.route('/demographics/<int:user_id>/<string:location_type>/<string:location_name>')
def demographics(user_id, location_type, location_name):
    # Validate location_type and fetch demographics accordingly
    if location_type.lower() == 'university':
        demographics_gender = fetch_demographics_by_university(location_name)
        demographics_age = fetch_age_distribution_by_university(location_name)
    elif location_type.lower() == 'city':
        demographics_gender = fetch_demographics_by_city(location_name)
        demographics_age = fetch_age_distribution_by_city(location_name)
    else:
        return render_template('error.html', message="Invalid location type for demographics.")

    gender_labels = [row[0] for row in demographics_gender]
    gender_values = [row[1] for row in demographics_gender]
    age_labels = [row[0] for row in demographics_age]
    age_values = [row[1] for row in demographics_age]

    return render_template(
        'demographics.html',
        user_id=user_id,
        location_type=location_type,
        location_name=location_name,
        gender_labels=gender_labels,
        gender_values=gender_values,
        age_labels=age_labels,
        age_values=age_values
    )

@app.route('/risk_profile/<int:user_id>')
def risk_profile(user_id):
    from db_connection import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT risk_profile, risk_cluster, updated_at FROM "Risk_Profile" WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return render_template('error.html', message="Risk profile not found for this user.")
    
    risk_profile_val, risk_cluster, updated_at = result
    
    # Define risk descriptions (adjust as needed)
    risk_descriptions = {
        0: "High Risk – Financially Vulnerable: You tend to overspend and may have negative cash flow.",
        1: "Low Risk – Financially Disciplined: You manage your finances well and maintain healthy savings.",
        2: "Moderate Risk – Budget Breakers: You sometimes exceed your budget, which could impact your savings.",
        3: "Moderate Risk – Savings Challenged: You stay within your budget, but your savings are minimal."
    }
    risk_description = risk_descriptions.get(risk_cluster, "Risk profile details not available.")
    
    return render_template(
        'dashboard.html',
        user_id=user_id,
        risk_profile=risk_profile_val,
        risk_description=risk_description,
        updated_at=updated_at
    )

@app.route('/risk_profile_fragment/<int:user_id>')
def risk_profile_fragment(user_id):
    from db_connection import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT risk_profile, risk_cluster, updated_at FROM "Risk_Profile" WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return "Risk profile not found."
    
    risk_profile_val, risk_cluster, updated_at = result
    
    risk_descriptions = {
        0: "High Risk – Financially Vulnerable: You tend to overspend and may have negative cash flow.",
        1: "Low Risk – Financially Disciplined: You manage your finances well and maintain healthy savings.",
        2: "Moderate Risk – Budget Breakers: You sometimes exceed your budget, which could impact your savings.",
        3: "Moderate Risk – Savings Challenged: You stay within your budget, but your savings are minimal."
    }
    risk_description = risk_descriptions.get(risk_cluster, "Risk profile details not available.")
    
    return render_template(
        'risk_profile_fragment.html',
        user_id=user_id,
        risk_profile=risk_profile_val,
        risk_description=risk_description,
        updated_at=updated_at
    )

@app.route('/financial_plan/<int:user_id>')
def financial_plan(user_id):
    # Retrieve user data (you may reuse your fetch_user_data function)
    result = fetch_user_data(user_id)
    if not result:
        return render_template('error.html', message="User data not found.")
    
    (user_id, name_stud, email, university, city, age, gender, monthly_budget, target_saving,
     grocery_expense, rent_expense, personal_expense, transportation_expense, misc_expense,
     tuition_due_date, insurance_due_date, income_amount) = result
     
    total_expense = grocery_expense + rent_expense + personal_expense + transportation_expense + misc_expense
    user_data = {
        'name_stud': name_stud,
        'university': university,
        'city': city,
        'monthly_budget': monthly_budget,
        'target_saving': target_saving,
        'wage_per_hour': income_amount / (20 * 4),  # or use a dedicated wage_per_hour field if available
        'total_expense': total_expense
    }
    
    # Retrieve risk profile data from Risk_Profile table
    from db_connection import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT risk_profile, risk_cluster, updated_at FROM "Risk_Profile" WHERE user_id = %s', (user_id,))
    risk_result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not risk_result:
        return render_template('error.html', message="Risk profile not found.")
    
    risk_profile_val, risk_cluster, updated_at = risk_result
    # Use your defined descriptions from earlier (or re-use the ones from your risk_profile route)
    risk_descriptions = {
        0: "High Risk – Financially Vulnerable: Your spending exceeds your income and you have negative savings.",
        1: "Low Risk – Financially Disciplined: You manage your finances well and maintain healthy savings.",
        2: "Moderate Risk – Budget Breakers: You sometimes exceed your budget, which could impact your savings.",
        3: "Moderate Risk – Savings Challenged: You stay within your budget, but your savings are minimal."
    }
    risk_description = risk_descriptions.get(risk_cluster, "Risk profile details not available.")
    
    # Generate the prompt
    prompt = generate_financial_plan_prompt(user_data, risk_profile_val, risk_description)
    
    # Use your AI inference client (this is similar to your ai_chatbot.py logic)
    try:
        # For example, using HuggingFace inference client:
        from huggingface_hub import InferenceClient
        api_key = os.getenv("HF_API_KEY")
        client = InferenceClient(provider="hf-inference", api_key=api_key)
        completion = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        plan = completion.choices[0].message.content.strip()
    except Exception as e:
        plan = f"Error generating financial plan: {e}"
    
    return render_template('financial_plan.html',
                           user_id=user_id,
                           financial_plan=plan,
                           risk_profile=risk_profile_val,
                           risk_description=risk_description,
                           updated_at=updated_at)

from flask import render_template
import os
from db_connection import get_db_connection
from fetch_data import fetch_user_data

# (Optionally, if not defined elsewhere, include the prompt-generation function)
def generate_financial_plan_prompt(user_data, risk_profile, risk_description):
    prompt = f"""
    You are a financial advisor AI. Below is the financial data of a university student:
    
    Name: {user_data['name_stud']}
    University: {user_data['university']}
    City: {user_data['city']}
    Monthly Budget: ${user_data['monthly_budget']:.2f}
    Target Savings: ${user_data['target_saving']:.2f}
    Hourly Wage: ${user_data['wage_per_hour']:.2f}
    Total Expense: ${user_data['total_expense']:.2f}
    
    Based on the above, their risk profile is: {risk_profile}.
    Explanation: {risk_description}.
    
    Now, please generate a personalized financial plan for this student that:
      1. Clearly states the risk profile.
      2. Explains why the student falls into this risk category.
      3. Provides actionable recommendations on how the student can improve their current financial situation, including strategies for generating additional income.
    
    The answer should be clear, concise, and actionable.
    """
    return prompt

@app.route('/payment_dates')
def payment_dates():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT tuition_fees_due_date, insurance_due_date FROM "Academic_Calendar_Event"')
    rows = cursor.fetchall()

    events = []
    for row in rows:
        tuition_date, insurance_date = row
        if tuition_date:
            events.append({
                'title': 'Tuition Fees Due',
                'start': tuition_date.strftime('%Y-%m-%d')
            })
        if insurance_date:
            events.append({
                'title': 'Insurance Due',
                'start': insurance_date.strftime('%Y-%m-%d')
            })

    cursor.close()
    conn.close()

    return render_template('payment_dates.html', events=events)

@app.route('/risk_profile_with_plan/<int:user_id>')
def risk_profile_with_plan(user_id):
    # --- Retrieve Risk Profile Data ---
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT risk_profile, risk_cluster, updated_at FROM "Risk_Profile" WHERE user_id = %s', 
        (user_id,)
    )
    risk_result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not risk_result:
        return "Risk profile not found."
    
    risk_profile_val, risk_cluster, updated_at = risk_result
    risk_descriptions = {
        0: "High Risk – Financially Vulnerable: Your spending exceeds your income and you have negative savings.",
        1: "Low Risk – Financially Disciplined: You manage your finances well and maintain healthy savings.",
        2: "Moderate Risk – Budget Breakers: You sometimes exceed your budget, which could impact your savings.",
        3: "Moderate Risk – Savings Challenged: You stay within your budget, but your savings are minimal."
    }
    risk_description = risk_descriptions.get(risk_cluster, "Risk profile details not available.")
    
    # --- Retrieve Additional User Financial Data ---
    result = fetch_user_data(user_id)
    if not result:
        return "User data not found."
    
    (user_id, name_stud, email, university, city, age, gender, monthly_budget, target_saving,
     grocery_expense, rent_expense, personal_expense, transportation_expense, misc_expense,
     tuition_due_date, insurance_due_date, income_amount) = result
     
    total_expense = grocery_expense + rent_expense + personal_expense + transportation_expense + misc_expense
    # If wage_per_hour is not directly available, we compute it from income_amount.
    # Adjust this as needed if you have a dedicated wage_per_hour field.
    wage_per_hour = income_amount / (20 * 4)
    
    user_data = {
        'name_stud': name_stud,
        'university': university,
        'city': city,
        'monthly_budget': monthly_budget,
        'target_saving': target_saving,
        'wage_per_hour': wage_per_hour,
        'total_expense': total_expense
    }
    
    # --- Generate the Prompt and Call the AI API ---
    prompt = generate_financial_plan_prompt(user_data, risk_profile_val, risk_description)
    
    try:
        from huggingface_hub import InferenceClient
        api_key = os.getenv("HF_API_KEY")
        client = InferenceClient(provider="hf-inference", api_key=api_key)
        completion = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        financial_plan = completion.choices[0].message.content.strip()
    except Exception as e:
        financial_plan = f"Error generating financial plan: {e}"
    
    # --- Render the Composite Fragment ---
    return render_template(
        'risk_profile_with_plan_fragment.html',
        user_id=user_id,
        risk_profile=risk_profile_val,
        risk_description=risk_description,
        updated_at=updated_at,
        financial_plan=financial_plan
    )

if __name__ == '__main__':
    app.run(debug=True)
