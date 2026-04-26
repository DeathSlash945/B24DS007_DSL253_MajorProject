import pandas as pd
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def run_analytics(file="steam_analysis.csv"):
    df = pd.read_csv(file)
    
    # Create the primary genre column
    df['primary_genre'] = df['genres'].str.split('|').str[0].fillna('Unknown')
    feature_cols = ['price', 'main_story', 'release_month', 'primary_genre', 'recommendations']
    target_col = 'overall_success_score'
    
    for col in ['price', 'main_story', 'release_month', 'recommendations', 'overall_success_score']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    X = df[feature_cols]
    y = df[target_col]
    
    print(f"Training on {len(df)} samples...")

    # OneHotEncoder implementation
    preprocessor = ColumnTransformer(
        transformers=[('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['primary_genre'])],
        remainder='passthrough'
    )
    
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    
    # Extract Feature Importance
    ohe_names = model.named_steps['preprocessor'].transformers_[0][1].get_feature_names_out()
    all_feature_names = list(ohe_names) + ['price', 'main_story', 'release_month', 'recommendations']
    importances = model.named_steps['regressor'].feature_importances_
    
    feat_data = sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
    
    # JSON converts Python 'None' to 'null', which is web-compliant
    json_safe_df = df.replace({np.nan: None})

    payload = {
        "genre_list": sorted(df['primary_genre'].unique().tolist()),
        "top_games": json_safe_df.sort_values(by='overall_success_score', ascending=False).head(600).to_dict(orient='records'),
        "feature_importance": [ {"feat": x[0], "val": float(x[1])} for x in feat_data ]
    }
    
    with open("dashboard_payload.json", "w") as f:
        # allow_nan=False ensures the output is valid for the HTML dashboard
        json.dump(payload, f, indent=4, allow_nan=False)
        
    print("Analytics payload generated successfully.")

if __name__ == "__main__":
    run_analytics()