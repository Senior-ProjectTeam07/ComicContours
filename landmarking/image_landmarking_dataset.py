# image_landmarking_dataset.py

import sys
import os
# Get the current directory and parent directory for importing modules
# This is done to allow importing modules from the parent directory
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

import glob
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

class ImageLandmarksDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.landmark_files = glob.glob(os.path.join(root_dir, '**', '*.pts'), recursive=True)
        self.transform = transform

    def __len__(self):
        return len(self.landmark_files)

    def __getitem__(self, idx):
        landmark_file = self.landmark_files[idx]
        landmarks = np.loadtxt(landmark_file, skiprows=3, comments=("version:", "n_points:", "{", "}"))
        landmarks = torch.tensor(landmarks.flatten(), dtype=torch.float32)
        image_file = landmark_file.replace('.pts', '.png')
        image = Image.open(image_file).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return landmarks, image