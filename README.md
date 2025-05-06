# Fintellect: AI-Powered Financial Planning for Students
## Overview
Fintellect is an AI-driven financial advisory platform tailored for students in American universities. It combines large language models, financial behavior clustering, and peer benchmarking to deliver personalized, adaptive, and actionable financial plans. The project was developed as part of a data analytics bachelor's thesis exploring how intelligent systems can improve student financial well-being.

## Key Features
* Risk Profiling: Clusters students based on financial behavior using K-Means (e.g., overspenders, savers).
* AI-Generated Financial Plans: Leverages Hugging Face’s Zephyr-7B model via Inference API for personalized advice.
* Peer Benchmarking: Compares student budgets and expenses to city/university averages.
* Interactive Dashboards: Visualizes income, savings, and spending behavior using Plotly.
* Financial Literacy Tools: Includes videos, simulators, and calculators for education and engagement.
* Goal Tracking: Visual indicators for meeting savings goals, with feedback from the system.
* Payment Calendar: Displays upcoming tuition and loan dates using FullCalendar.

## Tech Stack
### Frontend
* Jinja2 + Bootstrap + JavaScript
* Plotly (EDA & dynamic visuals)
* FullCalendar (payment schedule tab)

### Backend
* Python Flask (RESTful routes and business logic)
* PostgreSQL (data storage, student profiling)
* SQLAlchemy (ORM)

### AI Integration
* Hugging Face Inference API
* Model: HuggingFaceH4/zephyr-7b-beta

## How to Run Locally
1. Clone the Repository
```
git clone https://github.com/your-username/fintellect.git
cd fintellect
```

2. Set Up Environment
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure .env
```
DATABASE_URL=your_postgres_connection_string
HUGGINGFACE_API_KEY=your_hf_api_key
```

4. Run Flask App
```
python app.py
```



