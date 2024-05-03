# test_landmarks_to_style.py

import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

import unittest
import torch
from landmarking.landmarks_to_style import (
    LandmarksToExaggerationBlocks,
    ImageLandmarksDataset,
    train_one_epoch,
    validate,
)
from StyleCariGAN.model import Generator
from torch.utils.data import DataLoader
from torchvision import transforms
import os
import numpy as np

class TestLandmarksToStyle(unittest.TestCase):
    def setUp(self):
        # Set up basic configurations for testing
        self.num_landmarks = 68
        self.style_dim = 128
        self.num_blocks = 4
        self.n_latent = 512
        self.batch_size = 4
        
        # Set up a simple test dataset
        self.dataset = ImageLandmarksDataset(
            root_dir='data/300W',
            transform=transforms.Compose([
                transforms.Resize((128, 128)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ])
        )

        self.dataloader = DataLoader(self.dataset, batch_size=self.batch_size, shuffle=True)

        # Initialize the model and generator for testing
        self.mapping_network = LandmarksToExaggerationBlocks(
            self.num_landmarks, self.style_dim, self.num_blocks, self.n_latent
        )
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.mapping_network.to(device)
        self.style_generator = Generator(
            size=512,
            style_dim=self.style_dim,
            n_mlp=8,
        ).to(device)

    def test_landmarks_to_exaggeration_blocks(self):
        # Test the forward method of the model
        sample_landmarks = torch.rand(self.batch_size, self.num_landmarks * 2).cuda()
        output = self.mapping_network(sample_landmarks)

        correct_shape = (
            self.batch_size,
            self.num_blocks,
            self.n_latent // self.num_blocks,
        )
        
        # Check if the shape of the output tensor matches the expected shape
        self.assertEqual(output.shape, correct_shape)

    def test_image_landmarks_dataset(self):
        # Test if the dataset can be loaded and returns valid data
        sample_landmarks, sample_image = self.dataset[0]
        
        self.assertIsInstance(sample_landmarks, torch.Tensor)
        self.assertIsInstance(sample_image, torch.Tensor)

    def test_checkpoint_loading(self):
        # Test if the style generator checkpoint can be loaded
        checkpoint_path = 'test/checkpoint/001000.pt'  # Adjust as needed
        if os.path.exists(checkpoint_path):
            try:
                checkpoint = torch.load(checkpoint_path)
                self.style_generator.load_state_dict(checkpoint, strict=False)
            except Exception as e:
                self.fail(f"Failed to load checkpoint: {e}")

    def test_train_one_epoch(self):
        # Test the training process for one epoch
        optimizer = torch.optim.Adam(self.mapping_network.parameters(), lr=0.001)
        criterion = torch.nn.MSELoss()

        try:
            train_one_epoch(1, self.mapping_network, self.dataloader, optimizer, criterion, self.style_generator)
        except Exception as e:
            self.fail(f"Failed to train one epoch: {e}")

    def test_validation(self):
        # Test the validation process
        criterion = torch.nn.MSELoss()

        try:
            validate(1, self.mapping_network, self.dataloader, criterion, self.style_generator)
        except Exception as e:
            self.fail(f"Validation failed: {e}")


if __name__ == '__main__':
    unittest.main()
