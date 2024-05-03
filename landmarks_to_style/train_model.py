# train_model.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import warnings
import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler
from config import Config
import logging
from datetime import datetime
from landmarks_to_style.data_loader import get_dataloaders
from landmarks_to_style.model_loader import load_stylecarigan_generator, load_landmarkstostyles, load_cari_attribute_classifier
from landmarks_to_style.train import train
from landmarks_to_style.validate import validate
from landmarks_to_style.perceptual_loss import PerceptualLoss

# Suppress less critical warnings to streamline output
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.checkpoint")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data._utils.pin_memory")

# Configure environmental variables for optimized GPU utilization
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'backend:cudaMallocAsync,expandable_segments:True'
torch.backends.cudnn.benchmark = False  # Disable cudnn tuning to stabilize execution time
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Check and prepare CUDA device for operations
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == 'cuda':
    try:
        torch.cuda.synchronize()  # Ensure all CUDA operations are synchronized
        torch.cuda.empty_cache()  # Clear cached memory to minimize memory overhead
    except RuntimeError as e:
        logging.error(f"Failed to initialize CUDA: {e}")

def train_model():
    """
    Orchestrates the training process by setting up logging, data loaders, models,
    and running the training and validation cycles. This function encapsulates the
    entire process from setup to clean shutdown, ensuring all components are correctly
    configured and executed.
    """
    # Setup detailed logging for tracking and debugging
    now = datetime.now()
    log_filename = f'{Config.log_path}/training_{now.strftime("%Y%m%d_%H%M%S")}_landmarks_to_style.log'
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize data loaders for training and validation
    train_dataloader, val_dataloader = get_dataloaders(
        Config.dataset_path, Config.train_batch_size, Config.val_batch_size,
        Config.num_workers, Config.pin_memory
    )

    # Load models onto the specified compute device
    style_generator = load_stylecarigan_generator(
        Config.style_generator_ckpt_path, device, Config.style_dim, Config.n_mlp, Config.size
    ).to(device)

    landmarks_to_style = load_landmarkstostyles(
        Config.checkpoint_path, device, Config.input_size, Config.output_size,
        Config.hidden_layers, Config.numel
    ).to(device)

    cari_classifier = load_cari_attribute_classifier(Config.cari_attribute_ckpt_path, device)
    if cari_classifier:
        perceptual_loss = PerceptualLoss(cari_classifier)
    else:
        print("Failed to load the Cari-Attribute-Classifier.")

    # Early exit if models are not properly loaded
    if style_generator is None or landmarks_to_style is None:
        logging.error("Model loading failed, training cannot proceed.")
        return

    # Configure optimizer, loss function, and gradient scaler
    optimizer = torch.optim.Adam(landmarks_to_style.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    scaler = GradScaler()

    # Execute training and validation loops
    for epoch in range(Config.epochs):
        logging.info(f"Starting epoch {epoch+1} of {Config.epochs}")
        train_loss = train(epoch, landmarks_to_style, train_dataloader, optimizer,
                           perceptual_loss, style_generator, scaler, device)
        logging.info(f"Training loss for epoch {epoch+1}: {train_loss}")

        val_loss = validate(epoch, landmarks_to_style, val_dataloader, perceptual_loss, style_generator, device)
        logging.info(f"Validation loss for epoch {epoch+1}: {val_loss}")

        # Adjust the learning rate according to the schedule
        scheduler.step()

        # Periodically save the model's state
        if epoch % 10 == 0 or epoch == Config.epochs - 1:
            model_save_path = f'{Config.model_save_path}/landmarks_to_style_epoch_{epoch}.pth'
            torch.save(landmarks_to_style.state_dict(), model_save_path)

    # Save the final model state at the end of training
    final_model_path = f'{Config.model_save_path}/landmarks_to_style.pth'
    torch.save(landmarks_to_style.state_dict(), final_model_path)

if __name__ == '__main__':
    try:
        train_model()
    finally:
        logging.shutdown()  # Ensure all logging is flushed and handlers are closed properly