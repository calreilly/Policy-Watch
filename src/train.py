import torch
import torch.nn as nn
import torch.optim as optim
from data_processor import load_and_preprocess_data
from model import DraftPredictor

def train_model():
    print("Loading data...")
    train_loader, val_loader, test_loader, scaler, pos_encoder, team_encoder, input_dim = load_and_preprocess_data()
    num_teams = len(team_encoder.classes_)
    
    print(f"Input dim: {input_dim}, Num teams: {num_teams}")
    
    model = DraftPredictor(input_dim, num_teams)
    
    # Losses
    pick_criterion = nn.MSELoss()
    team_criterion = nn.CrossEntropyLoss()
    
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    
    # Weight for multi-task loss (loss = pick_loss * weight + team_loss)
    # Pick loss will be high initially (e.g. MSE for pick 200 = 40,000), 
    # team loss is log probabilities (~3.5 initially). 
    # We should weight them to be somewhat comparable.
    pick_weight = 0.01 
    
    epochs = 30
    print("Starting training...")
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        train_pick_loss, train_team_loss = 0, 0
        
        for X_batch, y_pick_batch, y_team_batch in train_loader:
            optimizer.zero_grad()
            
            pick_pred, team_pred = model(X_batch)
            
            loss_pick = pick_criterion(pick_pred, y_pick_batch)
            loss_team = team_criterion(team_pred, y_team_batch)
            
            loss = (pick_weight * loss_pick) + loss_team
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            train_pick_loss += loss_pick.item()
            train_team_loss += loss_team.item()
            
        # Validation
        model.eval()
        val_loss, val_pick_loss, val_team_loss = 0, 0, 0
        correct_teams = 0
        total_samples = 0
        
        with torch.no_grad():
            for X_batch, y_pick_batch, y_team_batch in val_loader:
                pick_pred, team_pred = model(X_batch)
                
                loss_pick = pick_criterion(pick_pred, y_pick_batch)
                loss_team = team_criterion(team_pred, y_team_batch)
                
                loss = (pick_weight * loss_pick) + loss_team
                
                val_loss += loss.item()
                val_pick_loss += loss_pick.item()
                val_team_loss += loss_team.item()
                
                # Accuracy for team prediction
                _, predicted_teams = torch.max(team_pred.data, 1)
                total_samples += y_team_batch.size(0)
                correct_teams += (predicted_teams == y_team_batch).sum().item()
                
        # Calculate averages for printing
        t_batches = len(train_loader)
        v_batches = len(val_loader)
        
        print(f"Epoch {epoch+1}/{epochs} | "
              f"Train Loss: {train_loss/t_batches:.3f} (Pick: {train_pick_loss/t_batches:.1f}, Team: {train_team_loss/t_batches:.3f}) | "
              f"Val Loss: {val_loss/v_batches:.3f} (Pick: {val_pick_loss/v_batches:.1f}, Team: {val_team_loss/v_batches:.3f}) | "
              f"Val Team Acc: {100 * correct_teams / total_samples:.2f}%")

    # Save model
    print("Saving model weights to 'draft_model.pth'...")
    torch.save(model.state_dict(), 'draft_model.pth')
    
if __name__ == "__main__":
    train_model()
