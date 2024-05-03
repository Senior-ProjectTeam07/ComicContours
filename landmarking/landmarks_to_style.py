# landmarks_to_style.py
import sys
import os

# Add the parent directory to the system path to allow module imports from the parent.
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

# Suppress specific warnings to reduce unnecessary output.
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.checkpoint")

import torch
import torch.nn as nn
import torch.optim
import argparse
import signal
import glob
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torch.utils.checkpoint import checkpoint_sequential  # Reduce memory usage for deep networks.
from torch.cuda.amp import autocast, GradScaler  # Enable mixed precision for efficiency.
from torchvision import transforms
import logging
from datetime import datetime
from StyleCariGAN.model import Generator  # GAN model for style generation.
from utils.file_utils import get_dir  # Utility to manage file paths.

# Set environment variables for efficient memory management.
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'backend:cudaMallocAsync,expandable_segments:True'
# Disable cuDNN benchmark to prevent excess memory usage when input sizes vary.
torch.backends.cudnn.benchmark = False
# Enable TensorFloat-32 (TF32) for improved GPU performance.
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Function to clear cached GPU memory to prevent memory buildup.
def clear_memory():
    torch.cuda.empty_cache()  # Release unused memory to keep usage low.

# Determine the device for computation (GPU or CPU).
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Define constants for the model input and output sizes.
input_size = 68 * 2  # Number of landmark coordinates (68 landmarks with x, y).
hidden_layers = 512  # Hidden layer size for the mapping network.
output_size = 128  # Style vector size matching StyleCariGAN.
numel = 1024  # Number of elements in the output tensor.

# Define a model for mapping landmarks to style vectors, with gradient checkpointing for reduced memory usage.
class LandmarksToStyles(nn.Module):
    def __init__(self, input_size, output_size, hidden_layers, numel):
        super().__init__()
        # Linear layer to map the input to hidden layers.
        self.linear = nn.Linear(input_size, hidden_layers)
        # List of sequential layers to create a deep network.
        self.numel = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_layers if i > 0 else input_size, hidden_layers),  # Linear layer.
                nn.ReLU(),  # Activation function.
                nn.Linear(hidden_layers, hidden_layers),  # Second linear layer.
                nn.ReLU(),  # Activation function.
                nn.Linear(hidden_layers, output_size if i == numel - 1 else hidden_layers),  # Output layer.
            )
            for i in range(numel)  # Create layers based on the specified number.
        ])

    def forward(self, style_tensor):
        style_tensor.requires_grad_()  # Enable gradient computation.
        # Use gradient checkpointing to reduce memory consumption.
        style_tensor = checkpoint_sequential(self.numel, segments=len(self.numel), input=style_tensor)
        # Flatten the output tensor to maintain consistent shape.
        return style_tensor.view(style_tensor.size(0), -1)

# Define a dataset for image landmarks with image preprocessing.
class ImageLandmarksDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir  # Base directory for the dataset.
        # Locate all landmark files in the dataset recursively.
        self.landmark_files = glob.glob(os.path.join(root_dir, '**', '*.pts'), recursive=True)
        self.transform = transform  # Apply transformations if provided.

    def __len__(self):
        return len(self.landmark_files)  # Return the number of samples.

    def __getitem__(self, idx):
        # Read landmarks from the corresponding file and convert to a flattened tensor.
        landmark_file = self.landmark_files[idx]
        landmarks = torch.tensor(
            np.loadtxt(landmark_file, skiprows=3, comments=("version:", "n_points:", "{", "}")).flatten(),
            dtype=torch.float32,
        )
        # Find the corresponding image file.
        image_file = landmark_file.replace('.pts', '.png')
        image = Image.open(image_file).convert('RGB')  # Load the image in RGB format.
        if self.transform:
            image = self.transform(image)  # Apply transformation if specified.
        return landmarks, image  # Return the landmarks and the image.

# Apply standard image transformations for the dataset.
image_transforms = transforms.Compose([
    transforms.Resize((128, 128)),  # Resize all images to 128x128.
    transforms.ToTensor(),  # Convert image to tensor format.
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # Normalize with given mean and std.
])

# Create the mapping network for the style conversion.
mapping_network = LandmarksToStyles(input_size, output_size, hidden_layers, numel).to(device)

# Initialize the StyleCariGAN generator for generating style vectors.
style_generator = Generator(size=512, style_dim=128, n_mlp=8).to(device)

# Load the checkpoint for the StyleCariGAN generator.
checkpoint_path = os.path.join(get_dir('StyleCariGAN/checkpoint/StyleCariGAN'), '001000.pt')
try:
    checkpoint = torch.load(checkpoint_path)  # Load the saved model checkpoint.
    model_dict = style_generator.state_dict()  # Get current state dictionary.
    valid_keys = {k: checkpoint[k] for k in model_dict.keys() if k in checkpoint}  # Keep valid keys.
    model_dict.update(valid_keys)  # Update the state dictionary with the valid keys.
    style_generator.load_state_dict(model_dict, strict=False)  # Load the checkpoint into the generator.
    print("StyleCariGAN's Generator checkpoint loaded successfully.")
except Exception as e:
    print(f"Error loading StyleCariGAN's Generator checkpoint: {e}")

# Create the dataset and dataloader with pin_memory for efficient data transfer to GPU.
dataset = ImageLandmarksDataset(get_dir('data/300W'), transform=image_transforms)  # Initialize the dataset.
# Split the dataset into training and validation subsets (80% training, 20% validation).
train_dataset, val_dataset = torch.utils.data.random_split(
    dataset, [int(len(dataset) * 0.8), len(dataset) - int(len(dataset) * 0.8)]
)

# Create the dataloaders for training and validation with multiple workers for faster data loading.
train_dataloader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=8, pin_memory=True)
val_dataloader = DataLoader(val_dataset, batch_size=4, shuffle=True, num_workers=8, pin_memory=True)

# Set the optimizer and loss function for training.
optimizer = torch.optim.SGD(mapping_network.parameters(), lr=0.1)  # Use SGD optimizer with a learning rate of 0.1.
criterion = nn.MSELoss()  # Mean squared error loss function.

# Initialize GradScaler for mixed precision to reduce memory usage during training.
scaler = GradScaler()  # Scale gradients to prevent underflow.

# Signal handler to save the state if the process is interrupted.
def signal_handler(sig, frame):
    torch.save(mapping_network.state_dict(), 'data/models/landmarks_to_style_interrupted.pth')  # Save model state.
    sys.exit(0)  # Exit the process.

signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler for interruptions.

# Define the training function with memory management.
def train(epoch, model, dataloader, optimizer, criterion, style_generator, scaler, verbose=False):
    model.train()  # Set the model to training mode.
    total_loss = 0  # Track the total loss for this epoch.

    for landmarks, images in dataloader:  # Loop through the batches in the dataloader.
        landmarks, images = landmarks.to(device), images.to(device)  # Transfer data to the GPU.

        model.zero_grad(set_to_none=True)  # Clear gradients to prevent buildup.
        
        # Get the latent style vectors from the StyleCariGAN generator.
        with torch.no_grad():
            target_styles = style_generator.get_latent(images)  # Get latent style vectors without gradients.
        
        with autocast():  # Enable mixed precision to reduce memory usage.
            predicted_styles = model(landmarks)  # Predict the style based on the landmarks.
            # Reshape and expand the tensor to match the expected dimensions.
            predicted_styles = predicted_styles.view(4, 1, 128, 1).expand(-1, 3, -1, 128)
            loss = criterion(predicted_styles, target_styles)  # Calculate the loss.
        
        scaler.scale(loss).backward()  # Scale and backpropagate the loss for gradient computation.
        scaler.unscale_(optimizer)  # Unscale gradients before the optimizer step.
        scaler.step(optimizer)  # Perform the optimizer step.
        scaler.update()  # Update the GradScaler.
        total_loss += loss.item()  # Accumulate the total loss for this epoch.

        # Free memory by deleting unused tensors.
        del landmarks, images, target_styles, predicted_styles, loss
        clear_memory()  # Clear cached memory to prevent buildup.

    print(f"Epoch {epoch}, Training Loss: {total_loss / len(dataloader)}")  # Output the training loss.

# Validation function to evaluate model performance and manage memory.
def validate(epoch, model, dataloader, criterion, style_generator, scaler, verbose=False):
    model.eval()  # Set the model to evaluation mode.
    total_loss = 0  # Track total validation loss for this epoch.

    with torch.no_grad():  # Disable gradient tracking during validation.
        for landmarks, images in dataloader:  # Loop through validation data.
            landmarks, images = landmarks.to(device), images.to(device)  # Transfer data to GPU.
            
            # Zero gradients to ensure clean state before evaluation.
            model.zero_grad(set_to_none=True)

            # Get latent style vectors from the generator to avoid memory buildup.
            target_styles = style_generator.get_latent(images)  # Obtain style vectors for validation.
            
            with autocast():  # Use mixed precision to reduce memory usage.
                predicted_styles = model(landmarks)  # Predict the styles for validation.
                # Expand the predicted styles to match expected dimensions.
                predicted_styles = predicted_styles.view(4, 1, 128, 1).expand(-1, 3, -1, 128)

                loss = criterion(predicted_styles, target_styles)  # Calculate the validation loss.
            
            total_loss += loss.item()  # Add to total loss.

            # Free memory by clearing unused tensors and cached memory.
            del landmarks, images, target_styles, predicted_styles, loss
            clear_memory()  # Clear cached memory to reduce memory usage.

    print(f"Epoch {epoch}, Validation Loss: {total_loss / len(dataloader)}")  # Output the validation loss.

# Main function to run training and validation loops.
if __name__ == '__main__':
    # Set up logging for both file and console output.
    now = datetime.now()  # Get the current date and time.
    now_str = now.strftime("%Y%m%d_%H%M%S")  # Format as string.
    logging.basicConfig(
        filename=f'training_{now_str}_landmarks_to_style.log',  # Log to file with timestamp.
        level=logging.INFO,  # Set the log level to INFO.
        format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log format.
    )

    # Add console logging for real-time output.
    console = logging.StreamHandler()  # Create a console handler.
    console.setLevel(logging.INFO)  # Set console logging to INFO level.
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Log format.
    console.setFormatter(formatter)  # Apply formatter to console logging.
    logging.getLogger('').addHandler(console)  # Add console handler to logger.

    # Parse command-line arguments.
    parser = argparse.ArgumentParser()  # Argument parser for command-line options.
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs')  # Training epochs.
    parser.add_argument('--lr', type=float, default=0.1, help='Learning rate')  # Learning rate.
    parser.add_argument('--batch_size', type=int, default=4, help='Batch size')  # Batch size for dataloader.
    args = parser.parse_args()  # Parse command-line arguments.

    # Try to load the model checkpoint if it exists.
    checkpoint_path = os.path.join(get_dir('data/models'), 'landmarks_to_style.pth')  # Checkpoint path.

    if os.path.exists(checkpoint_path):  # If checkpoint file exists, attempt to load it.
        try:
            mapping_network.load_state_dict(torch.load(checkpoint_path))  # Load the checkpoint.
            print(f"Loaded checkpoint from {checkpoint_path}")
        except (FileNotFoundError, RuntimeError) as e:  # Handle errors during checkpoint loading.
            print(f"Failed to load checkpoint from {checkpoint_path}. Reason: {e}")
    else:
        print(f"Checkpoint not found at {checkpoint_path}")  # Notify if checkpoint does not exist.

    # Training and validation loop over the specified number of epochs.
    for epoch in range(args.epochs):
        train(epoch, mapping_network, train_dataloader, optimizer, criterion, style_generator, scaler)
        validate(epoch, mapping_network, val_dataloader, criterion, style_generator, scaler)

        # Save checkpoint periodically and at the end of the training process.
        if epoch % 10 == 0:
            torch.save(mapping_network.state_dict(), f'data/models/landmarks_to_style_{epoch}.pth')  # Save checkpoint.

    # Save the final state of the model at the end of training.
    torch.save(mapping_network.state_dict(), 'data/models/landmarks_to_style.pth')  # Save final model state.