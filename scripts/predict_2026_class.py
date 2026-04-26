import os
import requests
import pandas as pd
import numpy as np
import torch
import nfl_data_py as nfl

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from data_processor import load_and_preprocess_data
from model import DraftPredictor

API_KEY = "LDxMtk3ML2DDrc4GzNipilXCwWQRlo8ElTZ179hSg+8QaVAnKzW56UePruFUhj4L"

def fetch_recent_ppa():
    headers = {"Authorization": f"Bearer {API_KEY}", "accept": "application/json"}
    all_ppa = []
    # Draft is 2026, so final seasons are 2024 or 2025
    for year in [2024, 2025]:
        url = f"https://api.collegefootballdata.com/ppa/players/season?year={year}"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            for p in resp.json():
                flat = {
                    "season": p["season"],
                    "name": p["name"],
                }
                if p.get("averagePPA"):
                    flat["avg_PPA_all"] = p["averagePPA"].get("all", 0.0)
                    flat["avg_PPA_pass"] = p["averagePPA"].get("pass", 0.0)
                    flat["avg_PPA_rush"] = p["averagePPA"].get("rush", 0.0)
                if p.get("totalPPA"):
                    flat["total_PPA_all"] = p["totalPPA"].get("all", 0.0)
                all_ppa.append(flat)
    
    df = pd.DataFrame(all_ppa)
    if not df.empty:
        # Keep the most recent season for each player
        df = df.sort_values('season', ascending=False).drop_duplicates(subset=['name'])
    return df

def generate_2026_mock():
    print("1. Fetching 2026 Combine Data...")
    combine_2026 = nfl.import_combine_data([2026])
    print(f"Loaded {len(combine_2026)} prospects from 2026 combine.")
    
    print("2. Fetching recent College PPA (2024-2025)...")
    cfbd_df = fetch_recent_ppa()
    
    if not cfbd_df.empty:
        # Merge on Name
        df = pd.merge(combine_2026, cfbd_df, left_on='player_name', right_on='name', how='left')
    else:
        df = combine_2026.copy()
        for c in ['avg_PPA_all', 'avg_PPA_pass', 'avg_PPA_rush', 'total_PPA_all']:
            df[c] = np.nan
            
    print("3. Preprocessing features...")
    # Get scalers and encoders from training pipeline
    old_cwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    _, _, _, scaler, pos_encoder, team_encoder, input_dim = load_and_preprocess_data()
    model_path = 'draft_model.pth'
    
    # Needs: ['ht', 'wt', 'forty', 'bench', 'vertical', 'broad_jump', 'cone', 'shuttle', 'avg_PPA_all', 'avg_PPA_pass', 'avg_PPA_rush', 'total_PPA_all'] + pos_dummies
    
    basic_features = ['ht', 'wt', 'forty', 'bench', 'vertical', 'broad_jump', 'cone', 'shuttle']
    advanced_features = ['avg_PPA_all', 'avg_PPA_pass', 'avg_PPA_rush', 'total_PPA_all']
    features_cols = basic_features + advanced_features
    
    def parse_height(ht_val):
        if pd.isna(ht_val): return np.nan
        if isinstance(ht_val, (int, float)): return float(ht_val)
        try:
            ht_str = str(ht_val)
            if '-' in ht_str:
                parts = ht_str.split('-')
                if len(parts) == 2:
                    return float(parts[0]) * 12 + float(parts[1])
            return float(ht_str)
        except ValueError:
            return np.nan
            
    df['ht'] = df['ht'].apply(parse_height)
    
    df['ht'] = df['ht'].fillna(df['ht'].median())
    df['wt'] = df['wt'].fillna(df['wt'].median())
    
    for f in basic_features[2:]:
        if f in df.columns:
            df[f] = df.groupby('pos')[f].transform(lambda x: x.fillna(x.median()) if not x.isna().all() else x)
            df[f] = df[f].fillna(df[f].median() if not pd.isna(df[f].median()) else 0.0)
        else:
            df[f] = 0.0
            
    for f in advanced_features:
        if f not in df.columns:
            df[f] = 0.0
        df[f] = df[f].fillna(0.0)
            
    # Load original data to rebuild exact dummy columns
    orig_df = pd.read_csv('data/combine_data.csv')
    pos_dummies_template = pd.get_dummies(orig_df['pos'], prefix='pos').iloc[0:0].copy()
    
    prospect_pos_dummies = pd.get_dummies(df['pos'], prefix='pos')
    
    # Align columns
    pos_dummies = pd.DataFrame(columns=pos_dummies_template.columns)
    for col in pos_dummies.columns:
        if col in prospect_pos_dummies.columns:
            pos_dummies[col] = prospect_pos_dummies[col]
        else:
            pos_dummies[col] = 0.0
            
    X_df = pd.concat([df[features_cols], pos_dummies], axis=1)
    
    X_scaled = scaler.transform(X_df)
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    
    print("4. Running Inference...")
    num_teams = len(team_encoder.classes_)
    model = DraftPredictor(input_dim, num_teams)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    with torch.no_grad():
        pick_pred, team_pred = model(X_tensor)
        
    df['predicted_pick'] = pick_pred.numpy()
    
    probabilities = torch.nn.functional.softmax(team_pred, dim=1)
    top_team_indices = torch.argmax(probabilities, dim=1)
    df['predicted_team'] = team_encoder.inverse_transform(top_team_indices.numpy())
    
    # Sort by predicted pick
    df = df.sort_values('predicted_pick').reset_index(drop=True)
    
    if not os.path.exists('results'):
        os.makedirs('results')
        
    output_path = 'results/2026_mock_draft.csv'
    df[['player_name', 'pos', 'school', 'predicted_pick', 'predicted_team']].to_csv(output_path, index=False)
    
    print("\n--- TOP 32 PICKS (ROUND 1 PROJECTION) ---")
    for i in range(min(32, len(df))):
        player = df.iloc[i]
        pick_int = int(round(player['predicted_pick']))
        # Filter out negative picks or extreme outliers
        if pick_int < 1: pick_int = 1
        print(f"#{pick_int} | {player['player_name']} ({player['pos']} - {player['school']}) -> {player['predicted_team']}")
        
    print(f"\nFull rankings saved to: {output_path}")

if __name__ == "__main__":
    generate_2026_mock()
