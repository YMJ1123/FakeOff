"""
Generate dummy data to make sure dataloader and model works
"""

import numpy as np
import torch

N = 5000
DIM = 1024

x = torch.randn(N, DIM)
y = torch.randint(0, 2, (N,))

torch.save({'x': x, 'y': y}, 'dummy_data.pt')

print(f"Generated dummy data: x shape {x.shape}, y shape {y.shape}")
print("Saved to dummy_data.pt")
