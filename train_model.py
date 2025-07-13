import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

# Sample training data
data = {
    'follow_up_days': [3, 7, 1, 10, 2, 5, 6],
    'has_company': [1, 0, 1, 1, 0, 1, 1],
    'status': ['won', 'lost', 'won', 'lost', 'lost', 'won', 'won']
}

df = pd.DataFrame(data)
df['status'] = df['status'].map({'lost': 0, 'won': 1})

X = df[['follow_up_days', 'has_company']]
y = df['status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model
dump(model, 'crm_model.joblib')
print("✅ Model trained and saved as crm_model.joblib")
