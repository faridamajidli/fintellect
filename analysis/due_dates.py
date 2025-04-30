from datetime import datetime

def format_due_date(date_value):
    """Format date values and handle missing data."""
    if date_value is None:
        return "N/A"
    return date_value.strftime("%Y-%m-%d")  # Ensure it's in a standard format

def check_due_status(due_date):
    """Returns 'red' if overdue, 'green' if upcoming."""
    today = datetime.today().strftime("%Y-%m-%d")
    return "red" if due_date != "N/A" and due_date < today else "green"