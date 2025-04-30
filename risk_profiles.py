import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from db_connection import get_db_connection
from sklearn.decomposition import PCA
import seaborn as sns
import psycopg2
from db_connection import get_db_connection


# Define a SQL query to retrieve the necessary data.
# Adjust the table/column names as needed.
query = """
SELECT 
    u.user_id,
    u.email,
    u.name_stud,
    u.gender,
    u.age,
    u.university,
    u.city,
    ef.ef_knowledge,  -- Now coming from Emergency_Fund
    b.monthly_budget,
    b.target_saving,
    pt.wage_per_hour,
    COALESCE(SUM(e.rent), 0) AS rent,
    COALESCE(SUM(e.grocery), 0) AS grocery,
    COALESCE(SUM(e.transportation), 0) AS transportation,
    COALESCE(SUM(e.personal), 0) AS personal,
    COALESCE(SUM(e.misc), 0) AS misc
FROM "User" u
LEFT JOIN "Budget" b ON u.user_id = b.user_id
LEFT JOIN "Expense" e ON u.user_id = e.user_id
LEFT JOIN "Emergency_Fund" ef ON u.user_id = ef.user_id
LEFT JOIN "Part_Time" pt ON u.user_id = pt.user_id
GROUP BY u.user_id, u.email, u.name_stud, u.gender, u.age, u.university, u.city, ef.ef_knowledge, b.monthly_budget, b.target_saving, pt.wage_per_hour;
"""

# Connect to the database and load the data into a DataFrame
conn = get_db_connection()
df = pd.read_sql(query, conn)
conn.close()

# Step 1: Calculate monthly income (assuming 20h/week * 4 weeks)
df['monthly_income'] = df['wage_per_hour'] * 20 * 4

# Step 2: Calculate total expense from the survey data
df['total_expense'] = df[['rent', 'grocery', 'transportation', 'personal', 'misc']].sum(axis=1)

# Step 3: Derived financial behavior features
df['spending_ratio']       = df['total_expense'] / df['monthly_income']
df['goal_savings_ratio']   = df['target_saving'] / df['monthly_income']
df['budget_discipline']    = df['total_expense'] / df['monthly_budget']
df['remaining_cash']       = df['monthly_income'] - df['total_expense']
df['actual_savings_ratio'] = df['remaining_cash'] / df['monthly_income']
df['overspending_flag']    = (df['total_expense'] > df['monthly_budget']).astype(int)
df['ef_knowledge_flag']    = df['ef_knowledge'].str.lower().map({'yes': 1, 'no': 0}).fillna(0)

# Define the features to be used for clustering
features = [
    'spending_ratio',      
    'goal_savings_ratio',   
    'actual_savings_ratio', 
    'budget_discipline',   
    'overspending_flag',
    'ef_knowledge_flag',    
    'remaining_cash'    
]

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# Experiment: Try different numbers of clusters
range_k = range(2, 11)  # testing from k=2 to k=10
silhouette_scores = []

print("Experimenting with different k values:")
for k in range_k:
    kmeans = KMeans(n_clusters=k, random_state=42)
    cluster_labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, cluster_labels)
    silhouette_scores.append(score)
    print(f"k = {k}: Silhouette Score = {score:.2f}")

chosen_k = 4
kmeans = KMeans(n_clusters=chosen_k, random_state=42)
df['risk_cluster'] = kmeans.fit_predict(X_scaled)
score = silhouette_score(X_scaled, df['risk_cluster'])
print(f"Chosen k = {chosen_k} produces Silhouette Score: {score:.2f}")

# Compute and display cluster means for the chosen features
cluster_means = df.groupby('risk_cluster')[features].mean().round(2)
print("Cluster Means for k=4:\n", cluster_means)

risk_labels = {
    0: "High Risk – Financially Vulnerable",        # Cluster 0
    1: "Low Risk – Financially Disciplined",        # Cluster 1
    2: "Moderate Risk – Budget Breakers",           # Cluster 2
    3: "Moderate Risk – Savings Challenged"         # Cluster 3
}

df['risk_profile'] = df['risk_cluster'].map(risk_labels)

# Display a sample of the risk profiles
print(df[['user_id', 'risk_cluster', 'risk_profile']].head())

# Visualise the clusters
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=df['risk_cluster'], palette='Set1')
plt.title("Student Risk Clusters (PCA)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend(title='Cluster')
plt.grid(True)
plt.show()

# Saving these profiles into PostgreSQL
conn = get_db_connection()
cursor = conn.cursor()

for idx, row in df.iterrows():
    cursor.execute("""
        INSERT INTO "Risk_Profile" (user_id, risk_profile, risk_cluster)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET 
            risk_profile = EXCLUDED.risk_profile,
            risk_cluster = EXCLUDED.risk_cluster,
            updated_at = CURRENT_TIMESTAMP;
    """, (row['user_id'], row['risk_profile'], row['risk_cluster']))
conn.commit()
cursor.close()
conn.close()





# Plot the silhouette scores
#plt.figure(figsize=(8, 4))
#plt.plot(range_k, silhouette_scores, marker='o')
#plt.xlabel("Number of clusters (k)")
#plt.ylabel("Silhouette Score")
#plt.title("Silhouette Score for Different Values of k")
#plt.grid(True)
#plt.show()

# Choose a value for k based on the plot; here we'll continue with k=3 as an example
#chosen_k = 3
#kmeans = KMeans(n_clusters=chosen_k, random_state=42)
#df['risk_cluster'] = kmeans.fit_predict(X_scaled)
#score = silhouette_score(X_scaled, df['risk_cluster'])
#print(f"Chosen k = {chosen_k} produces Silhouette Score: {score:.2f}")

# Map clusters to risk profile labels based on the cluster means
#cluster_means = df.groupby('risk_cluster')[features].mean().round(2)
#print("Cluster Means:\n", cluster_means)

# Based on the cluster means observed previously,
# reassign risk labels to better match the data.
#risk_labels = {
    #0: "High Risk – Financially Vulnerable",
    #1: "Moderate Risk – Budget Breakers",
    #2: "Low Risk – Financially Disciplined"
#}
#df['risk_profile'] = df['risk_cluster'].map(risk_labels)

# Display a sample of the risk profiles
#print(df[['user_id', 'risk_cluster', 'risk_profile']].head())