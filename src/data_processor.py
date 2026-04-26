import os
import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch.utils.data import Dataset, DataLoader

class NFLDraftDataset(Dataset):
    def __init__(self, X, y_pick, y_team):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y_pick = torch.tensor(y_pick, dtype=torch.float32)
        self.y_team = torch.tensor(y_team, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y_pick[idx], self.y_team[idx]


def load_and_preprocess_data(data_path="data/combine_data.csv", test_size=0.15, val_size=0.15):
    """
    Loads combine data, handles missing values, and prepares it for modeling.
    Returns dataloaders and necessary encoders.
    """
    df = pd.read_csv(data_path)
    
    # Load and merge advanced CFBD stats
    try:
        df_ppa = pd.read_csv("data/cfbd_ppa.csv")
        # Match by name and season (draft_year - 1)
        df['cfb_season'] = df['draft_year'] - 1
        df = pd.merge(
            df, 
            df_ppa, 
            left_on=['player_name', 'cfb_season'], 
            right_on=['name', 'season'], 
            how='left'
        )
    except FileNotFoundError:
        print("Warning: cfbd_ppa.csv not found, proceeding without advanced stats.")
        # Create dummy columns
        for c in ['avg_PPA_all', 'avg_PPA_pass', 'avg_PPA_rush', 'total_PPA_all']:
            df[c] = np.nan
    
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
    
    # Target Handling
    # Fill undrafted players
    df['draft_ovr'] = df['draft_ovr'].fillna(260)
    df['draft_team'] = df['draft_team'].fillna('Undrafted')
    
    # Feature Selection and Imputation
    basic_features = ['ht', 'wt', 'forty', 'bench', 'vertical', 'broad_jump', 'cone', 'shuttle']
    advanced_features = ['avg_PPA_all', 'avg_PPA_pass', 'avg_PPA_rush', 'total_PPA_all']
    features = basic_features + advanced_features
    
    # Impute height and weight globally if missing
    df['ht'] = df['ht'].fillna(df['ht'].median())
    df['wt'] = df['wt'].fillna(df['wt'].median())
    
    # Impute combine metrics by position group
    for feature in basic_features[2:]:
        # Use position group median, if still NaN use global median
        df[feature] = df.groupby('pos')[feature].transform(lambda x: x.fillna(x.median()))
        df[feature] = df[feature].fillna(df[feature].median())
        
    # Impute advanced stats
    for feature in advanced_features:
        # If defensive player, they might not have PPA right now, fill with 0
        df[feature] = df[feature].fillna(0.0)
        
    # Categorical features - Position and School
    pos_encoder = LabelEncoder()
    df['pos_encoded'] = pos_encoder.fit_transform(df['pos'].astype(str))
    
    # School might have too many dimensions, but let's encode it anyway.
    school_encoder = LabelEncoder()
    df['school_encoded'] = school_encoder.fit_transform(df['school'].astype(str))
    
    # Target Encoders
    team_encoder = LabelEncoder()
    df['team_encoded'] = team_encoder.fit_transform(df['draft_team'].astype(str))
    
    # Select columns for X
    # One-hot encoding position would be better than label encoding for NN, but embeddings can work too.
    # For simplicity, we will one-hot encode position
    pos_dummies = pd.get_dummies(df['pos'], prefix='pos')
    
    X_df = pd.concat([df[features], pos_dummies], axis=1)
    
    # Scale numerical features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_df)
    
    y_pick = df['draft_ovr'].values
    y_team = df['team_encoded'].values
    
    # Train / Val / Test Split
    X_train, X_temp, y_pick_train, y_pick_temp, y_team_train, y_team_temp = train_test_split(
        X_scaled, y_pick, y_team, test_size=(test_size + val_size), random_state=42
    )
    
    val_ratio = val_size / (test_size + val_size)
    X_val, X_test, y_pick_val, y_pick_test, y_team_val, y_team_test = train_test_split(
        X_temp, y_pick_temp, y_team_temp, test_size=(1 - val_ratio), random_state=42
    )

    # Dataloaders
    batch_size = 64
    train_dataset = NFLDraftDataset(X_train, y_pick_train, y_team_train)
    val_dataset = NFLDraftDataset(X_val, y_pick_val, y_team_val)
    test_dataset = NFLDraftDataset(X_test, y_pick_test, y_team_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader, scaler, pos_encoder, team_encoder, X_df.shape[1]

if __name__ == "__main__":
    train_loader, val_loader, test_loader, scaler, pos_encoder, team_encoder, input_dim = load_and_preprocess_data()
    print(f"Input dimensions: {input_dim}")
    print(f"Number of target teams: {len(team_encoder.classes_)}")
    for x, y_p, y_t in train_loader:
        print("X batch shape:", x.shape)
        print("Y pick batch shape:", y_p.shape)
        print("Y team batch shape:", y_t.shape)
        break    
