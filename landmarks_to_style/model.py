# model.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    def __init__(self, features):
        super(ResidualBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Linear(features, features),
            nn.BatchNorm1d(features),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(features, features),
            nn.BatchNorm1d(features)
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        residual = x
        out = self.block(x)
        out += residual  # Element-wise addition
        out = self.relu(out)
        return out

class LandmarksToStyles(nn.Module):
    def __init__(self, input_size, output_size, hidden_layers, numel):
        super().__init__()
        self.initial = nn.Sequential(
            nn.Linear(input_size, hidden_layers),
            nn.ReLU(inplace=True)
        )
        self.res_blocks = nn.Sequential(*[ResidualBlock(hidden_layers) for _ in range(numel)])
        self.final = nn.Linear(hidden_layers, output_size)

    def forward(self, x):
        x = self.initial(x)
        x = self.res_blocks(x)
        x = self.final(x)
        return x