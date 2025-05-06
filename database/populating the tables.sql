-- Insert Users
INSERT INTO "User" (name_stud, email, university, city, age, gender)
SELECT name_stud, email, university, city, age, gender 
FROM staging_users;

-- Insert Budget Data
INSERT INTO "Budget" (user_id, monthly_budget, target_saving)
SELECT u.user_id, s.monthly_budget, s.target_saving
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert Expense Data
INSERT INTO "Expense" (user_id, grocery, rent, personal, transportation, misc)
SELECT u.user_id, s.grocery, s.rent, s.personal, s.transportation, s.misc
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert Academic Calendar Event Data
INSERT INTO "Academic_Calendar_Event" (user_id, tuition_fees_due_date, insurance_due_date)
SELECT u.user_id, s.tuition_fees_due_date, s.insurance_due_date
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert Emergency Fund Data
INSERT INTO "Emergency_Fund" (user_id, ef_knowledge, ef_amount)
SELECT u.user_id, s.ef_knowledge, s.target_saving * 0.5
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert Local Student Deals Data
INSERT INTO "Local_Student_Deals" (user_id, subway, starbucks, tacobell, walmart)
SELECT u.user_id, s.subway, s.starbucks, s.tacobell, s.walmart
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert User Preferences
INSERT INTO "User_Preferences" (user_id, notification_preferences)
SELECT u.user_id, s.notification_preferences
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert Part-Time Work Data
INSERT INTO "Part_Time" (user_id, wage_per_hour)
SELECT u.user_id, s.wage_per_hour
FROM staging_users s
JOIN "User" u ON s.email = u.email;

-- Insert Income Data (Monthly Income = wage_per_hour * 20 hours * 4 weeks)
INSERT INTO "Income" (user_id, income_amount)
SELECT u.user_id, (s.wage_per_hour * 20 * 4)
FROM staging_users s
JOIN "User" u ON s.email = u.email;
