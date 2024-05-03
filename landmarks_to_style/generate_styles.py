# generate_styles.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch

def generate_style_vectors(model, dataloader, device):
    # Ensure the model is in evaluation mode
    model.eval()

    style_vectors = []

    # Iterate through the dataloader
    for landmarks, image in dataloader:
        image = image.to(device)
        landmarks = landmarks.to(device)

        # Generate the style vectors
        with torch.no_grad():
            style_vector = model(landmarks)
            style_vectors.append(style_vector)
    
    # Clear unnecessary tensors from memory to maintain a low memory footprint.
    del landmarks, image, style_vector
    torch.cuda.empty_cache()  # Helps in avoiding CUDA out of memory errors.

    return torch.cat(style_vectors, dim=0)