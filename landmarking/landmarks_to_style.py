# landmarks_to_style.py

import sys
import os
# Get the current directory and parent directory for importing modules
# This is done to allow importing modules from the parent directory
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from utils.file_utils import get_dir
from StyleCariGAN.model import Generator
import signal
import numpy as np
import glob
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch.nn as nn
import argparse
import logging
from datetime import datetime

class LandmarksToStyleBlocks(nn.Module):
    def __init__(self, num_landmarks, style_dim, num_blocks, n_latent):
        super().__init__()
        self.num_blocks = num_blocks
        self.style_dim = style_dim
        self.n_latent = n_latent
        # Use a ModuleList to hold the blocks so that PyTorch can keep track of the parameters
        self.blocks = nn.ModuleList([nn.Sequential(
            nn.Linear(num_landmarks * 2, 512),  # Linear layer to reduce dimensionality
            nn.ReLU(),  # ReLU activation for non-linearity
            nn.Linear(512, style_dim)  # Linear layer to get the desired style dimension
        ) for _ in range(num_blocks)])  # Repeat for the number of style blocks
        
    def forward(self, landmarks):
        # Apply each block to the landmarks
        styles = [block(landmarks) for block in self.blocks]
        # Concatenate the style blocks along the feature dimension
        style_tensor = torch.cat(styles, dim=1)
        # Reshape the style blocks to match the expected latent dimension size
        style_tensor = style_tensor.view(-1, self.num_blocks, self.n_latent // self.num_blocks)
        return style_tensor

class ImageLandmarksDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        # Use glob to get all the landmark files in the directory and subdirectories
        self.landmark_files = glob.glob(os.path.join(root_dir, '**', '*.pts'), recursive=True)
        self.transform = transform

    def __len__(self):
        # The length of the dataset is the number of landmark files
        return len(self.landmark_files)

    def __getitem__(self, idx):
        # Load the landmarks from the file
        landmark_file = self.landmark_files[idx]
        landmarks = np.loadtxt(landmark_file, skiprows=3, comments=("version:", "n_points:", "{", "}"))
        landmarks = torch.tensor(landmarks.flatten(), dtype=torch.float32)
        # Load the corresponding image
        image_file = landmark_file.replace('.pts', '.png')
        image = Image.open(image_file).convert('RGB')
        # Apply the transform to the image if one is provided
        if self.transform:
            image = self.transform(image)
        return landmarks, image

# Resize the images to 128x128, convert them to tensors, and normalize them to the range [-1, 1]
image_transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# Check if a GPU is available and if not, use a CPU
# This allows the code to run on a machine without a GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Create the dataset and dataloader
dataset = ImageLandmarksDataset(root_dir=get_dir('data/300W'), transform=image_transform)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

# Create the mapping network with 68 landmarks, style_dim of 512 for each style block, 4 style blocks, and n_latent of 512
mapping_network = LandmarksToStyleBlocks(68, 512, 4, 512)

# --- Define the optimizer and loss function --- 
# Use Adam optimizer for its balance of speed and performance
optimizer = torch.optim.Adam(mapping_network.parameters(), lr=0.001)
# Use MSE loss as it's suitable for regression problems
criterion = nn.MSELoss()

# Create the generator with the appropriate parameters
style_generator = Generator(
    size=128,  # The size of the generated images
    style_dim=512,  # The dimension of the style vector
    n_mlp=8,  # The number of layers in the MLP that produces the style vectors
).to(device)  # Move the generator to the GPU if available

# Load the pre-trained weights into the generator
style_generator.load_state_dict(torch.load(os.path.join(get_dir('StyleCariGAN/checkpoint/StyleCariGAN'), '001000.pt')))

# Get the images from the dataset
images = torch.stack([image for _, image in dataset])

# Move the images to the GPU if available
images = images.to(device)

# Run the images through the generator to get the target styles
target_styles = style_generator.get_latent(images)

# Split the dataset into training and validation sets
num_items = len(dataset)
# Use 80% of the data for training and the rest for validation
num_train = round(num_items * 0.8)
num_val = num_items - num_train
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [num_train, num_val])

# Use multiple dataloader workers for faster data loading for the training and validation sets
train_dataloader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=8)
val_dataloader = DataLoader(val_dataset, batch_size=4, shuffle=True, num_workers=8)

# Move the model to the GPU if available
mapping_network = mapping_network.to(device)

# Move the target styles to the GPU if available
target_styles = [target_style.to(device) for target_style in target_styles]

# Training and validation functions
def train_one_epoch(epoch, model, dataloader, optimizer, criterion, generator):
    model.train()  # Set the model to training mode
    total_loss = 0
    for landmarks, images in dataloader:
        landmarks = landmarks.to(device)  # Move landmarks to GPU
        images = images.to(device)  # Move images to GPU
        optimizer.zero_grad()  # Zero the gradients
        style_blocks = model(landmarks)  # Forward pass
        # Run the images through the generator to get the target styles
        target_styles = generator.get_latent(images)
        # Reshape target styles to match the output of the model
        target = target_styles.view(-1, model.num_blocks, model.n_latent // model.num_blocks)
        loss = criterion(style_blocks, target)  # Compute the loss
        loss.backward()  # Backward pass
        optimizer.step()  # Update the weights
        total_loss += loss.item()  # Accumulate the loss
    # Print the average loss for this epoch
    print(f"Epoch {epoch}, Training Loss: {total_loss / len(dataloader)}")

def validate(epoch, model, dataloader, criterion, generator):
    model.eval()  # Set the model to evaluation mode
    total_loss = 0
    with torch.no_grad():  # No need to compute gradients in evaluation mode
        for landmarks, images in dataloader:
            landmarks = landmarks.to(device)  # Move landmarks to GPU
            images = images.to(device)  # Move images to GPU
            style_blocks = model(landmarks)  # Forward pass
            # Run the images through the generator to get the target styles
            target_styles = generator.get_latent(images)
            # Reshape target styles to match the output of the model
            target = target_styles.view(-1, model.num_blocks, model.n_latent // model.num_blocks)
            loss = criterion(style_blocks, target)  # Compute the loss
            total_loss += loss.item()  # Accumulate the loss
    # Print the average loss for this epoch
    print(f"Epoch {epoch}, Validation Loss: {total_loss / len(dataloader)}")

# Define a handler for the SIGINT signal
def signal_handler(sig, frame):
    print('Interrupted by user. Saving model...')
    torch.save(mapping_network.state_dict(), 'data/models/landmarks_to_style_blocks_interrupted.pth')
    print('Model saved. Exiting...')
    sys.exit(0)

# Register the handler for the SIGINT signal
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    # Get the current date and time
    now = datetime.now()

    # Format as a string
    now_str = now.strftime("%Y%m%d_%H%M%S")

    # Use a file with the current date and time in the name to avoid overwriting previous logs
    logging.basicConfig(filename=f'training_{now_str}_landmarks_to_style_blocks.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Add a StreamHandler to root logger to allow the logs to be printed to the console as well as the file
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # Command line args to define # of epochs, learning rate, and batch size to be specified when running the script
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size')
    args = parser.parse_args()

    # Use arguments from above to train the model
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    optimizer = torch.optim.Adam(mapping_network.parameters(), lr=args.lr)

    # Load the model's state if a checkpoint exists from resuming from a checkpoint
    print("Attempting to load checkpoint...")
    checkpoint_path = os.path.join(get_dir('data/models'), 'landmarks_to_style_blocks.pth')
    print(f"Checkpoint path: {checkpoint_path}")
    if os.path.exists(checkpoint_path):
        try:
            mapping_network.load_state_dict(torch.load(checkpoint_path))
            print(f"Loaded checkpoint from {checkpoint_path}")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")

    # Training loop with validation
    for epoch in range(args.epochs):
        train_one_epoch(epoch, mapping_network, train_dataloader, optimizer, criterion, style_generator)
        validate(epoch, mapping_network, val_dataloader, criterion, style_generator)

        # Save the model's state periodically
        if epoch % 10 == 0:
            torch.save(mapping_network.state_dict(), f'data/models/landmarks_to_style_blocks_{epoch}.pth')

    # Save the final model
    torch.save(mapping_network.state_dict(), 'data/models/landmarks_to_style_blocks.pth')