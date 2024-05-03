# train.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import torch
from torch.cuda.amp import autocast

def train(epoch, model, dataloader, optimizer, perceptual_loss, feature_extractor, scaler, device):
    model.train()  # Ensure the model is in training mode.
    total_loss = 0

    for landmarks, org_images, gan_images in dataloader:
        # Move data to the specified device.
        landmarks = landmarks.to(device)
        org_images = org_images.to(device)
        gan_images = gan_images.to(device)

        optimizer.zero_grad(set_to_none=True)  # Zero out the gradients to prevent accumulation.

        # Compute features for the original and GAN-generated images without tracking gradients
        with torch.no_grad():
            org_features = feature_extractor(org_images)
            gan_features = feature_extractor(gan_images)

        # Perform forward pass and compute loss in a mixed precision context
        with autocast():
            predicted_styles = model(landmarks)
            loss_org = perceptual_loss(predicted_styles, org_features)  # Compare to original image features
            loss_gan = perceptual_loss(predicted_styles, gan_features)  # Compare to GAN-generated features
            loss = (loss_org + loss_gan) / 2  # Average the losses

        # Backpropagate the loss and update model weights
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()  # Accumulate the loss for averaging.

        # Clear unnecessary tensors from memory to maintain a low memory footprint.
        del landmarks, org_images, gan_images, org_features, gan_features, loss

    average_loss = total_loss / len(dataloader)  # Calculate the average loss over all batches
    print(f"Epoch {epoch}, Training Loss: {average_loss}")  # Output the average loss for the epoch
    return average_loss