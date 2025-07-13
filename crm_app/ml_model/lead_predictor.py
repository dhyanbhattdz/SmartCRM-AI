import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model():
    data = pd.read_csv('leads_data.csv')  # you must create this
    X = data[['feature1', 'feature2']]
    y = data['converted']
    model = RandomForestClassifier()
    model.fit(X, y)
    joblib.dump(model, 'crm_app/ml_model/model.pkl')
