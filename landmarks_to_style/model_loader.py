# model_loader.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch
import torch.nn as nn
from StyleCariGAN.exaggeration_model import StyleCariGAN, LayerSwapGenerator  # StyleCariGAN class
from landmarks_to_style.model import LandmarksToStyles
from StyleCariGAN.model import ResNet18

def load_stylecarigan_generator(ckpt_path, device, style_dim=128, n_mlp=8, size=512):
    """
    Load and initialize the StyleCariGAN generator model from a checkpoint.
    
    This function ensures that the model is loaded onto the specified device (e.g., CPU or GPU) 
    and that its weights are initialized from a checkpoint file if available. It handles errors 
    gracefully, returning None if the checkpoint file does not exist or an error occurs during loading.

    Args:
        ckpt_path (str): Path to the saved model checkpoint file.
        device (torch.device): Device to load the model onto.
        style_dim (int): Dimensionality of the style vector (default 128).
        n_mlp (int): Number of MLP layers in the generator (default 8).
        size (int): Size of the generator's input (default 512).

    Returns:
        torch.nn.Module or None: The loaded and initialized generator model, or None if an error occurs.
    """
    model = LayerSwapGenerator(size=size, style_dim=style_dim, n_mlp=n_mlp).to(device)
    
    if not os.path.exists(ckpt_path):
        print(f"Error: The file {ckpt_path} does not exist.")
        return None

    try:
        checkpoint = torch.load(ckpt_path, map_location=device)
        model_dict = model.state_dict()
        valid_keys = {k: v for k, v in checkpoint.items() if k in model_dict and model_dict[k].shape == checkpoint[k].shape}
        model_dict.update(valid_keys)
        model.load_state_dict(model_dict, strict=False)
        model.eval()
        print("StyleCariGAN's Generator loaded successfully with valid keys.")
    except Exception as e:
        print(f"An error occurred while loading StyleCariGAN's model: {e}")
        return None

    return model

def load_stylecarigan(ckpt_path, device, size=256, style_dim=512, n_mlp=8, channel_multiplier=2):
    """
    Load and initialize the StyleCariGAN model from a checkpoint.

    This function prepares the StyleCariGAN model for inference or continued training by loading
    its state from a checkpoint file. It ensures that all tensors are moved to the specified device and
    that the model is correctly configured before applying the state.

    Args:
        ckpt_path (str): Path to the checkpoint file containing model weights.
        device (torch.device): Device to load the model onto.
        size (int): The size of images for the generator (default 256).
        style_dim (int): Dimensionality of the style vector (default 512).
        n_mlp (int): Number of layers in MLP (default 8).
        channel_multiplier (int): Channel multiplier for generator (default 2).

    Returns:
        torch.nn.Module or None: The loaded model, or None if an error occurs.
    """
    model = StyleCariGAN(size=size, style_dim=style_dim, n_mlp=n_mlp, channel_multiplier=channel_multiplier).to(device)

    if not os.path.exists(ckpt_path):
        print(f"Error: The file {ckpt_path} does not exist.")
        return None

    try:
        checkpoint = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(checkpoint['g_ema'], strict=False)  # Load the generator's weights
        model.eval()
        print("StyleCariGAN model loaded successfully.")
    except Exception as e:
        print(f"An error occurred while loading the StyleCariGAN model: {e}")
        return None

    return model

def load_landmarkstostyles(ckpt_path, device, input_size=136, output_size=128, hidden_layers=512, numel=1024):
    """
    Load and initialize the LandmarksToStyles model from a checkpoint.

    This function prepares the model for inference or continued training by loading its state
    from a checkpoint file. It ensures that all tensors are moved to the specified device and 
    that only valid state keys are updated.

    Args:
        ckpt_path (str): Path to the checkpoint file containing model weights.
        device (torch.device): Device to load the model onto.
        input_size (int): Number of input features (default 136).
        output_size (int): Dimensionality of the output (default 128).
        hidden_layers (int): Number of neurons in each hidden layer (default 512).
        numel (int): Number of elements or modules in the model (default 1024).

    Returns:
        torch.nn.Module or None: The loaded model, or None if an error occurs.
    """
    model = LandmarksToStyles(input_size=input_size, output_size=output_size, hidden_layers=hidden_layers, numel=numel).to(device)

    if not os.path.exists(ckpt_path):
        print(f"Error: The file {ckpt_path} does not exist.")
        return None

    try:
        checkpoint = torch.load(ckpt_path, map_location=device)
        model_dict = model.state_dict()
        valid_keys = {k: v for k, v in checkpoint.items() if k in model_dict and model_dict[k].shape == checkpoint[k].shape}
        model_dict.update(valid_keys)
        model.load_state_dict(model_dict, strict=False)
        model.eval()
        print("LandmarksToStyles model loaded successfully with valid keys.")
    except Exception as e:
        print(f"An error occurred while loading the model: {e}")
        return None

    return model

def load_cari_attribute_classifier(ckpt_path, device):
    """
    Load and initialize the Cari-Attribute-Classifier model from a checkpoint.
    
    This function ensures that the classifier is loaded onto the specified device (e.g., CPU or GPU)
    and that its weights are initialized from a checkpoint file if available. It handles errors 
    gracefully, returning None if the checkpoint file does not exist or an error occurs during loading.

    Args:
        ckpt_path (str): Path to the saved model checkpoint file.
        device (torch.device): Device to load the model onto.

    Returns:
        torch.nn.Module or None: The loaded and initialized classifier model, or None if an error occurs.
    """
    # Assuming the classifier is based on ResNet18
    model = ResNet18()
    model.fc = nn.Identity()  # Replace the final fully connected layer with an identity to use as a feature extractor

    if not os.path.exists(ckpt_path):
        print(f"Error: The file {ckpt_path} does not exist.")
        return None

    try:
        checkpoint = torch.load(ckpt_path, map_location=device)
        print("Keys in the checkpoint:", checkpoint.keys())
        # model.load_state_dict(checkpoint['state_dict'])
        model_dict = model.state_dict()
        valid_keys = {k: v for k, v in checkpoint.items() if k in model_dict and model_dict[k].shape == checkpoint[k].shape}
        model_dict.update(valid_keys)
        model.load_state_dict(model_dict, strict=False)
        model.to(device)
        model.eval()
        print("Cari-Attribute-Classifier loaded successfully.")
    except Exception as e:
        print(f"An error occurred while loading the Cari-Attribute-Classifier model: {e}")
        return None

    return model