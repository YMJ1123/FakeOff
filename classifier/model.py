
from .loss.focal_loss import FocalLoss
from .loss.focal_loss_adaptive_gamma import FocalLossAdaptive

import torch
import torch.nn as nn


class EmbClassifier(nn.Module):
    def __init__(self, 
                 input_dim=1024, 
                 hidden_dim=256,
                 n_class=2):
        super(EmbClassifier, self).__init__()
        
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(num_features=hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(num_features=hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, n_class)
        )

    def forward(self, x):
        return self.model(x)
