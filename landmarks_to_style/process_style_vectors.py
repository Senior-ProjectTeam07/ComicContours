# process_style_vectors.py

import sys
import os
# Get the current directory and parent directory for importing modules
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from utils.file_utils import get_dir
import torch
import numpy as np
import glob
from StyleCariGAN.exaggeration_model import StyleCariGAN
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

# Load pre-trained weights into the StyleCariGAN generator
style_cari_gan = StyleCariGAN(...)
style_cari_gan.load_state_dict(torch.load('StyleCariGAN/checkpoint/StylCariGAN/001000.pt'))
style_cari_gan.eval()

# Assuming the use of transforms to match the GAN's expected input
image_transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

class ImageDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.image_files = glob.glob(os.path.join(root_dir, '**', '*.png'), recursive=True)
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_file = self.image_files[idx]
        image = Image.open(image_file).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image
    
dataset = ImageDataset(root_dir=get_dir('data/300W'), transform=image_transform)
dataset_loader = DataLoader(dataset, batch_size=4, shuffle=True)

with torch.no_grad():
    for batch_images in dataset_loader:
        # Forward pass through the generator
        generated_data = style_cari_gan(batch_images)

        # Extract the style vectors. Replace '...' with the actual key or method to obtain the style vector
        style_vector_batch = generated_data[...].cpu().numpy()
        style_vectors.append(style_vector_batch)

# Define a transform to process the images in the way StyleCariGAN expects
transform = transforms.Compose([
    transforms.Resize((1024, 1024)),  # or the size your StyleCariGAN expects
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])


# Process each image in the 300W dataset
style_vectors = []
for image_path in image_paths:  # You need to define image_paths to point to your 300W dataset images
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        style_vector = model(image, return_latents=True)  # This function call may differ based on the actual StyleCariGAN implementation
    style_vectors.append(style_vector.cpu().numpy())

# Convert the list of style vectors to a single numpy array
style_vectors = np.array(style_vectors)

# Save the style vectors for later use
np.save('style_vectors_300W.npy', style_vectors)
