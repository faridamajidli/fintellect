import plotly.express as px
from plotly.io import to_html
import pandas as pd

def generate_expense_charts(grocery, rent, personal, transportation, misc):
    """Generate bar and pie charts for expense distribution."""
    
    expense_data = pd.DataFrame({
        "Category": ["Grocery", "Rent", "Personal", "Transportation", "Miscellaneous"],
        "Amount": [grocery, rent, personal, transportation, misc]
    })

    # Stacked Bar Chart
    bar_chart = px.bar(expense_data, x="Category", y="Amount", title="Expense Breakdown",
                       color="Category", text="Amount")
    bar_chart_html = to_html(bar_chart, full_html=False)

    # Pie Chart
    pie_chart = px.pie(expense_data, names="Category", values="Amount",
                       title="Expense Distribution")
    pie_chart_html = to_html(pie_chart, full_html=False)

    return bar_chart_html, pie_chart_html