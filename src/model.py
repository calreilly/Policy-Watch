import torch
import torch.nn as nn

class DraftPredictor(nn.Module):
    def __init__(self, input_dim, num_teams, hidden_dim=128):
        super(DraftPredictor, self).__init__()
        
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Dropout(0.3)
        )
        
        # Regression head for overall draft pick
        self.pick_head = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1) # Predicts one continuous value
        )
        
        # Classification head for predicting the team
        self.team_head = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, num_teams) # Predicts logits for cross entropy
        )

    def forward(self, x):
        shared_features = self.shared(x)
        pick_pred = self.pick_head(shared_features)
        team_logits = self.team_head(shared_features)
        
        return pick_pred.squeeze(), team_logits
