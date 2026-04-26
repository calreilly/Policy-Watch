import torch
import pandas as pd
import numpy as np
from data_processor import load_and_preprocess_data
from model import DraftPredictor

def predict_prospect(prospect_data, model_path='draft_model.pth'):
    # Load scalers and encoders
    _, _, _, scaler, pos_encoder, team_encoder, input_dim = load_and_preprocess_data()
    
    # Initialize model
    num_teams = len(team_encoder.classes_)
    model = DraftPredictor(input_dim, num_teams)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # We need to construct the feature vector exactly how it was trained
    # Features: ['ht', 'wt', 'forty', 'bench', 'vertical', 'broad_jump', 'cone', 'shuttle'] + pos_dummies
    
    # Make a dummy dataframe with the same pos structure
    df = pd.read_csv('data/combine_data.csv')
    df['ht'] = df['ht'].fillna(74.0) # dummy
    pos_dummies_template = pd.get_dummies(df['pos'], prefix='pos').iloc[0:1].copy()
    for col in pos_dummies_template.columns:
        pos_dummies_template[col] = 0.0
        
    for k, v in prospect_data.items():
        if isinstance(v, dict):
            # Pos is a categorical
            pos_col = f"pos_{v['pos']}"
            if pos_col in pos_dummies_template.columns:
                pos_dummies_template[pos_col] = 1.0
                
    features = [
        prospect_data.get('ht', 74.0),
        prospect_data.get('wt', 215.0),
        prospect_data.get('forty', 4.5),
        prospect_data.get('bench', 15.0),
        prospect_data.get('vertical', 35.0),
        prospect_data.get('broad_jump', 120.0),
        prospect_data.get('cone', 7.1),
        prospect_data.get('shuttle', 4.2),
        prospect_data.get('avg_PPA_all', 0.0),
        prospect_data.get('avg_PPA_pass', 0.0),
        prospect_data.get('avg_PPA_rush', 0.0),
        prospect_data.get('total_PPA_all', 0.0)
    ]
    
    feature_df = pd.DataFrame([features], columns=['ht', 'wt', 'forty', 'bench', 'vertical', 'broad_jump', 'cone', 'shuttle', 'avg_PPA_all', 'avg_PPA_pass', 'avg_PPA_rush', 'total_PPA_all'])
    feature_df = pd.concat([feature_df, pos_dummies_template.reset_index(drop=True)], axis=1)
    
    # Scale
    X_scaled = scaler.transform(feature_df)
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    
    with torch.no_grad():
        pick_pred, team_pred = model(X_tensor)
        
    pick = int(pick_pred.item())
    
    # Get top 3 probable teams
    probabilities = torch.nn.functional.softmax(team_pred, dim=1).squeeze()
    top_3_idx = torch.argsort(probabilities, descending=True)[:3]
    top_3_teams = [(team_encoder.inverse_transform([idx])[0], probabilities[idx].item() * 100) for idx in top_3_idx]
    
    return pick, top_3_teams

if __name__ == "__main__":
    # Example Prospect (Caleb Williams / generic QB profile)
    generic_qb = {
        'ht': 73.0,
        'wt': 215.0,
        'forty': 4.58,
        'bench': 15.0, 
        'vertical': 32.0,
        'broad_jump': 115.0,
        'cone': 7.0,
        'shuttle': 4.15,
        'avg_PPA_all': 1.1,
        'avg_PPA_pass': 1.1,
        'avg_PPA_rush': 0.1,
        'total_PPA_all': 35.0,
        'pos': {'pos': 'QB'}
    }
    
    print("Predicting Generic QB Profile...")
    pick, teams = predict_prospect(generic_qb)
    print(f"Predicted Pick: {pick}")
    print(f"Most Probable Teams (Top 3):")
    for team, prob in teams:
        print(f" - {team}: {prob:.2f}%")
