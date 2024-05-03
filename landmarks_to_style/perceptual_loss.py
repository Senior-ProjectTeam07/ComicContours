# perceptual_loss.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch
import torch.nn as nn
import torch.nn.functional as F

class PerceptualLoss(nn.Module):
    def __init__(self, feature_extractor):
        super().__init__()
        self.feature_extractor = feature_extractor
        for param in self.feature_extractor.parameters():
            param.requires_grad = False  # Freeze the feature extractor

    def forward(self, predicted, target):
        predicted_features = self.feature_extractor(predicted)
        target_features = self.feature_extractor(target)
        loss = F.mse_loss(predicted_features, target_features)
        return loss