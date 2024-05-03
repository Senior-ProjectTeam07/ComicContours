# data_loader.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import glob
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch

class ImageLandmarksDataset(Dataset):
    """
    A dataset class for loading image and landmark data for style transfer training.

    Attributes:
        root_dir (str): The root directory from which to load landmarks and corresponding images.
        landmark_files (list): A list of file paths for all landmark files.
        transform (callable, optional): Optional transform to be applied on a sample.

    Methods:
        __len__: Returns the number of items in the dataset.
        __getitem__: Retrieves an image and its corresponding landmarks by index.
    """

    def __init__(self, root_dir, transform=None):
        """
        Initializes the dataset by listing all landmark files in the root directory.

        Args:
            root_dir (str): The directory containing landmark files and corresponding images.
            transform (callable, optional): A function/transform to apply to the images.
        """
        self.root_dir = root_dir
        self.landmark_files = glob.glob(os.path.join(root_dir, '**', '*.pts'), recursive=True)
        self.transform = transform
        # Filter out landmarks that do not have a corresponding generated image
        self.landmark_files = [f for f in self.landmark_files if os.path.exists(f.replace('.pts', '_gan.png'))]

    def __len__(self):
        """
        Returns:
            int: The total number of landmark files.
        """
        return len(self.landmark_files)

    def __getitem__(self, idx):
        """
        Retrieves the images and landmarks at the specified index.

        Args:
            idx (int): The index of the item.

        Returns:
            tuple: (landmarks, org_image, gan_image) where all three are tensors.
        """
        landmark_file = self.landmark_files[idx]
        landmarks = torch.tensor(
            np.loadtxt(landmark_file, skiprows=3, comments=("version:", "n_points:", "{", "}")).flatten(),
            dtype=torch.float32,
        )
        image_file = landmark_file.replace('.pts', '.png')
        org_image = Image.open(image_file).convert('RGB')
        gan_image = Image.open(image_file.replace('.png', '_gan.png')).convert('RGB')
        
        if self.transform:
            org_image = self.transform(org_image)
            gan_image = self.transform(gan_image)

        return landmarks, org_image, gan_image

def get_transforms():
    """
    Defines and returns a composed transform for image processing.

    Returns:
        torchvision.transforms.Compose: A series of transforms to apply to images.
    """
    return transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])

def get_dataloaders(root_dir, train_batch_size=4, val_batch_size=4, num_workers=8, pin_memory=True, single_set=False):
    transform = get_transforms()
    dataset = ImageLandmarksDataset(root_dir, transform=transform)

    if single_set:
        return DataLoader(dataset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers, pin_memory=pin_memory)
    
    else:
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

        train_dataloader = DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True,
                                    num_workers=num_workers, pin_memory=pin_memory)
        val_dataloader = DataLoader(val_dataset, batch_size=val_batch_size, shuffle=False,
                                    num_workers=num_workers, pin_memory=pin_memory)

        return train_dataloader, val_dataloader