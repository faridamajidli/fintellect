def generate_financial_plan_prompt(user_data, risk_profile, risk_description):
    """
    Generate a detailed prompt for the financial advisor using the user's data,
    risk profile, and risk description. Instruct the financial advisor to produce HTML output
    with headings and bullet points for improved readability.

    The prompt instructs the financial advisor to:
      1. Clearly state your risk profile.
      2. Explain why you fall into that risk category.
      3. Provide three actionable, conversational recommendations on how to improve your financial situation,
         including ideas for generating additional income. Consider that the university and city are located in America;
         include any state-specific opportunities (like local job markets, regional financial aid programs, or state-sponsored loans)
         and mention university-specific loans or financial assistance available at your institution.

    The response should be clear, concise, and written using conversational pronouns (e.g., "you", "your").
    """
    prompt = f"""
    You are a financial advisor. Your task is to produce a personalized financial plan
    in valid HTML, using headings (<h2>, <h3>) and bullet points (<ul><li>) to structure the response.
    Please address the user in a conversational tone, using "you" and "your."

    Below is the student's financial data:
      - University: {user_data['university']} (in America)
      - City: {user_data['city']} (in America)
      - Monthly Budget: ${user_data['monthly_budget']:.2f}
      - Target Savings: ${user_data['target_saving']:.2f}
      - Hourly Wage: ${user_data['wage_per_hour']:.2f}
      - Total Expense: ${user_data['total_expense']:.2f}

    Risk Profile: {risk_profile}
    Explanation: {risk_description}

    Please format your answer in **three main sections**, each with an HTML heading:
      1. <h2>Risk Profile</h2>
         - Clearly state the user's risk profile.
      2. <h2>Why You Fall Into This Category</h2>
         - Explain why the user has this risk profile, referencing their budget, savings, and expenses.
      3. <h2>Recommendations for Improvement</h2>
         - Provide exactly three bullet points (<ul><li>) of actionable steps the user can take to improve their financial situation.
         - Include ideas for generating additional income in their city and state.
         - Mention any university-specific loans or grants relevant to {user_data['university']}.
    
    Use the following guidelines:
      - Output valid HTML only (no Markdown).
      - Use headings (<h2>, <h3>) for each main section.
      - Use <ul> and <li> for the bullet points in the recommendations section.
      - Address the user in a friendly, conversational tone, using "you" and "your."
      - Keep paragraphs relatively short for readability.

    Return only the HTML code for your final answer. Do not include any extra explanations or disclaimers.
    """
    return prompt
