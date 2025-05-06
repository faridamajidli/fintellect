CREATE TABLE IF NOT EXISTS public."User"
(
    user_id SERIAL PRIMARY KEY,
    name_stud VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    university VARCHAR(255),
    city VARCHAR(255),
    age INTEGER,
    gender VARCHAR(25)
);

CREATE TABLE IF NOT EXISTS public."Expense"
(
    expense_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    grocery NUMERIC,
    rent NUMERIC,
    personal NUMERIC,
    transportation NUMERIC,
    misc NUMERIC,
    total_expense NUMERIC GENERATED ALWAYS AS (grocery + rent + personal + transportation + misc) STORED
);

CREATE TABLE IF NOT EXISTS public."Budget"
(
    budget_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    monthly_budget NUMERIC,
    target_saving NUMERIC
);

CREATE TABLE IF NOT EXISTS public."Emergency_Fund"
(
    emergency_fund_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    ef_amount NUMERIC,
    ef_knowledge VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS public."Academic_Calendar_Event"
(
    event_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    tuition_fees_due_date DATE,
    insurance_due_date DATE
);

CREATE TABLE IF NOT EXISTS public."Local_Student_Deals"
(
    deal_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    subway VARCHAR(255),
    starbucks VARCHAR(255),
    tacobell VARCHAR(255),
    walmart VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS public."User_Preferences"
(
    preferences_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    notification_preferences VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS public."Part_Time"
(
    user_id INTEGER REFERENCES public."User" (user_id),
    wage_per_hour NUMERIC
);

CREATE TABLE IF NOT EXISTS public."Income"
(
    income_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public."User" (user_id),
    income_amount NUMERIC
);