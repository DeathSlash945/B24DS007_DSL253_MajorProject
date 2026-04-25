import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def run_analytics(file="steam_analysis.csv"):
    df = pd.read_csv(file)
    
    # Create the primary genre column
    df['primary_genre'] = df['genres'].str.split('|').str[0]
    # Define the exact columns the model will use
    feature_cols = ['price', 'main_story', 'release_month', 'primary_genre']
    target_col = 'overall_success_score'
    
    # Filter the dataframe to remove rows where ANY of these features are NaN
    #clean_df = df.dropna(subset=feature_cols + [target_col])
    clean_df=df.fillna('NAN')
    
    X = clean_df[feature_cols]
    y = clean_df[target_col]
    
    print(f"Training on {len(clean_df)} valid samples (Dropped {len(df) - len(clean_df)} rows with missing data)")

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
    
    # Extract Feature Importance (Same as before)
    ohe_names = model.named_steps['preprocessor'].transformers_[0][1].get_feature_names_out()
    all_feature_names = list(ohe_names) + ['price', 'main_story', 'release_month']
    importances = model.named_steps['regressor'].feature_importances_
    
    feat_data = sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True)[:10]
    
    # Package for Dashboard (Using the original df for the top_games list to keep all data)
    payload = {
        "genre_list": sorted(df['primary_genre'].fillna('Action').unique().tolist()),
        "top_games": df.sort_values(by='overall_success_score', ascending=False).head(1000).to_dict(orient='records'),
        "feature_importance": [ {"feat": x[0], "val": float(x[1])} for x in feat_data ]
    }
    
    with open("dashboard_payload.json", "w") as f:
        json.dump(payload, f)
    print("Analytics payload generated successfully.")