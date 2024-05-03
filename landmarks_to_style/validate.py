# validate.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch
from torch.cuda.amp import autocast

def validate(epoch, model, dataloader, perceptual_loss, feature_extractor, device):
    model.eval()  # Switch the model to evaluation mode.
    total_loss = 0

    with torch.no_grad():  # Turn off gradients, as they are not needed for validation.
        for landmarks, org_images, gan_images in dataloader:
            # Move data to the specified device.
            landmarks = landmarks.to(device)
            org_images = org_images.to(device)
            gan_images = gan_images.to(device)

            # Compute features for the original and GAN-generated images
            org_features = feature_extractor(org_images)
            gan_features = feature_extractor(gan_images)

            with autocast():  # Use mixed precision for faster computation.
                predicted_styles = model(landmarks)
                loss_org = perceptual_loss(predicted_styles, org_features)  # Compute loss for original image features
                loss_gan = perceptual_loss(predicted_styles, gan_features)  # Compute loss for GAN-generated features
                loss = (loss_org + loss_gan) / 2  # Average the losses

            total_loss += loss.item()  # Accumulate loss for averaging

    avg_loss = total_loss / len(dataloader)  # Calculate the average loss over all batches
    print(f"Epoch {epoch}, Validation Loss: {avg_loss}")  # Display the calculated average loss
    return avg_loss