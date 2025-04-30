from huggingface_hub import InferenceClient
from ai_budget_recommendations import generate_budget_recommendations
from fetch_data import fetch_user_data
import os

# Set your HF API key as an environment variable or paste it here temporarily
api_key = os.getenv("HF_API_KEY")  # or replace with your key as a string

# Initialize the Inference Client
client = InferenceClient(
    provider="hf-inference",
    api_key=api_key
)

def generate_financial_plan(user_id):
    result = fetch_user_data(user_id)
    if not result:
        return "No financial data found for this user."

    # Unpack based on updated structure including income_amount
    user_id, name_stud, email, university, city, age, gender, monthly_budget, target_saving, \
    grocery_expense, rent_expense, personal_expense, transportation_expense, misc_expense, \
    tuition_due_date, insurance_due_date, income_amount = result

    # Convert numerical values safely
    monthly_budget = float(monthly_budget)
    target_saving = float(target_saving)
    income_amount = float(income_amount)
    grocery_expense = float(grocery_expense)
    rent_expense = float(rent_expense)
    personal_expense = float(personal_expense)
    transportation_expense = float(transportation_expense)
    misc_expense = float(misc_expense)

    # Calculate totals
    total_expense = grocery_expense + rent_expense + personal_expense + transportation_expense + misc_expense
    total_saving = (monthly_budget + income_amount) - total_expense

    # Get recommendations
    recommendations = generate_budget_recommendations(user_id)
    recommendation_text = "\n".join(recommendations["university"] + recommendations["city"])

    # Prepare prompt for AI
    prompt = f"""
    You are a financial advisor AI helping a university student manage their finances.

    User: {name_stud}, Email: {email}, Age: {age}, Gender: {gender}, University: {university}, City: {city}
    Monthly Budget: ${monthly_budget:.2f}, Monthly Income: ${income_amount:.2f}, 
    Target Saving: ${target_saving:.2f}
    Total Expense: ${total_expense:.2f}, Total Savings: ${total_saving:.2f}
    Tuition Due Date: {tuition_due_date}, Insurance Due Date: {insurance_due_date}

    Budget Recommendations:
    {recommendation_text}

    Based on this information, provide a detailed financial plan to help the student:
    - Optimize savings
    - Reduce unnecessary expenses
    - Reach short- and long-term financial goals
    """

    try:
        completion = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating financial plan: {e}"