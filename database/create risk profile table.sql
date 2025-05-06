CREATE TABLE IF NOT EXISTS "Risk_Profile" (
  user_id INTEGER PRIMARY KEY,
  risk_profile TEXT,
  risk_cluster INTEGER,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
