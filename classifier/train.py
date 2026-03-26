import argparse
import os

import torch
import torch.nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.nn import functional as F

from .focal_loss import FocalLoss
from .focal_loss_adaptive_gamma import FocalLossAdaptive
from .model import EmbClassifier
from .data import DummyDataset
from .Metrics.metrics import (
    expected_calibration_error,
    maximum_calibration_error,
    adaptive_expected_calibration_error,
    test_classification_net
)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--n_epochs", type=int, default=10)
    parser.add_argument("--check_cal_every", type=int, default=1)
    parser.add_argument("--val_every", type=int, default=2)
    parser.add_argument("--save_every", type=int, default=5)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--gamma", type=float, default=2.0)
    parser.add_argument("--adaptive", action="store_true")
    parser.add_argument("--no_focal", action="store_true", help="Disable focal loss and use cross-entropy instead")
    parser.add_argument("--train_path", type=str, default="train_data.pt")
    parser.add_argument("--val_path", type=str, default="val_data.pt")
    parser.add_argument("--save_dir", type=str, default="classifier/checkpoints")
    parser.add_argument("--hidden_dim", type=int, default=512)
    parser.add_argument("--n_bins", type=int, default=15)
    return parser.parse_args()


def train(
        hidden_dim,
        batch_size,
        n_epochs,
        lr,
        adaptive,
        no_focal,
        gamma,
        train_path,
        val_path,
        save_dir,
        check_cal_every=1,
        val_every=2,
        save_every=5,
        n_bins=15,
        device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
):
    # Create save directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Load separate train and validation datasets
    train_dataset = DummyDataset(train_path)
    val_dataset = DummyDataset(val_path)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    model = EmbClassifier(input_dim=1024, hidden_dim=hidden_dim, n_class=2).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    
    # Choose loss function
    if no_focal:
        loss_fn = torch.nn.CrossEntropyLoss()
        print("Using Cross-Entropy Loss")
    else:
        loss_fn = FocalLossAdaptive(gamma=gamma, device=device) \
            if adaptive else FocalLoss(gamma=gamma)
        loss_type = "Adaptive Focal Loss" if adaptive else "Focal Loss"
        print(f"Using {loss_type} with gamma={gamma}")
    
    # Training loop
    for ep in range(n_epochs):
        model.train()
        total_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {ep + 1}/{n_epochs}, Train Loss: {avg_loss:.4f}")
        
        # Validation
        if (ep + 1) % val_every == 0:
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device)
                    logits = model(batch_x)
                    loss = loss_fn(logits, batch_y)
                    val_loss += loss.item()
            
            avg_val_loss = val_loss / len(val_loader)
            conf_matrix, accuracy, _, _, _ = test_classification_net(model, val_loader, device)
            print(f"  Validation - Loss: {avg_val_loss:.4f}, Accuracy: {accuracy:.4f}")
        
        # Calibration check
        if (ep + 1) % check_cal_every == 0:
            model.eval()
            all_confs = []
            all_preds = []
            all_labels = []
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device)
                    logits = model(batch_x)
                    softmax = F.softmax(logits, dim=1)
                    confidences, predictions = torch.max(softmax, dim=1)
                    
                    all_confs.extend(confidences.cpu().numpy().tolist())
                    all_preds.extend(predictions.cpu().numpy().tolist())
                    all_labels.extend(batch_y.cpu().numpy().tolist())
            
            # Calculate all three calibration metrics
            ece = expected_calibration_error(all_confs, all_preds, all_labels, num_bins=n_bins)
            mce = maximum_calibration_error(all_confs, all_preds, all_labels, num_bins=n_bins)
            aece = adaptive_expected_calibration_error(all_confs, all_preds, all_labels, num_bins=n_bins)
            
            print(f"  Calibration - ECE: {ece:.4f}, MCE: {mce:.4f}, Adaptive ECE: {aece:.4f}")
        
        # Save checkpoint
        if (ep + 1) % save_every == 0:
            checkpoint_path = os.path.join(save_dir, f"model_epoch_{ep + 1}.pt")
            torch.save({
                'epoch': ep + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': avg_loss,
            }, checkpoint_path)
            print(f"  Saved checkpoint to {checkpoint_path}")
    
    # Save final model
    final_path = os.path.join(save_dir, "model_final.pt")
    torch.save({
        'epoch': n_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_loss': avg_loss,
    }, final_path)
    print(f"Saved final model to {final_path}")
    print("Training complete!")
    return model


if __name__ == '__main__':
    args = get_args()
    model = train(
        hidden_dim=args.hidden_dim,
        batch_size=args.batch_size,
        n_epochs=args.n_epochs,
        lr=args.lr,
        adaptive=args.adaptive,
        no_focal=args.no_focal,
        gamma=args.gamma,
        train_path=args.train_path,
        val_path=args.val_path,
        save_dir=args.save_dir,
        check_cal_every=args.check_cal_every,
        val_every=args.val_every,
        save_every=args.save_every,
        n_bins=args.n_bins
    )
