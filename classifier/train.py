import argparse

import torch
import torch.nn
import torch.optim as optim
from torch.utils.data import DataLoader

from .focal_loss import FocalLoss
from .focal_loss_adaptive_gamma import FocalLossAdaptive
from .model import EmbClassifier
from .data import DummyDataset


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--n_epochs", type=int, default=10)
    parser.add_argument("--check_cal_every", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--gamma", type=float, default=2.0)
    parser.add_argument("--adaptive", action="store_true")
    parser.add_argument("--data_path", type=str, default="dummy_data.pt")
    parser.add_argument("--hidden_dim", type=int, default=512)
    return parser.parse_args()


def train(
        hidden_dim,
        batch_size,
        n_epochs,
        lr,
        adaptive,
        gamma,
        data_path,
        check_cal_every=1,
        device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
):
    # Initialize dataset and dataloader
    dataset = DummyDataset(data_path)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model = EmbClassifier(input_dim=1024, hidden_dim=hidden_dim, n_class=2).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    loss_fn = FocalLossAdaptive(gamma=gamma, device=device) \
        if adaptive else FocalLoss(gamma=gamma, device=device)
    
    # Training loop
    for ep in range(n_epochs):
        model.train()
        total_loss = 0.0
        
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        
        if (ep + 1) % check_cal_every == 0:
            print(f"Epoch {ep + 1}/{n_epochs}, Loss: {avg_loss:.4f}")
    
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
        gamma=args.gamma,
        data_path=args.data_path,
        check_cal_every=args.check_cal_every
    )
