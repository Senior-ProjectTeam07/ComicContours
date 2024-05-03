# config.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
from utils.file_utils import get_dir

class Config:
    """
    Configuration settings for the training and validation of the landmarks to style model.

    Attributes:
        train_batch_size (int): Batch size for training.
        val_batch_size (int): Batch size for validation.
        lr (float): Learning rate for the optimizer.
        epochs (int): Number of epochs to train the model.
        size (int): Size parameter of the StyleCariGAN generator.
        style_dim (int): Dimensionality of the style vector.
        n_mlp (int): Number of MLP layers in the StyleCariGAN generator.
        image_size (tuple): Dimensions to which all images will be resized.
        input_size (int): Total input features (number of landmarks * 2).
        output_size (int): Dimensionality of the output style vector.
        hidden_layers (int): Number of neurons in each hidden layer.
        numel (int): Number of elements (layers) in the neural network model.
        num_workers (int): Number of subprocesses to use for data loading.
        pin_memory (bool): Whether to use pinned (page-locked) memory.
        checkpoint_path (str): Path to the training checkpoint file.
        model_save_path (str): Directory where trained models will be saved.
        style_generator_ckpt_path (str): Path to the StyleCariGAN generator checkpoint file.
        dataset_path (str): Directory containing the training and validation datasets.
        log_path (str): Directory to save log files.
    """
    train_batch_size = 4
    val_batch_size = 4
    lr = 0.1
    epochs = 3
    size = 512
    style_dim = 128
    n_mlp = 8
    generate_size=256
    generate_style_dim=512
    channel_multiplier=2
    image_size = (128, 128)
    input_size = 68 * 2  # Assuming each landmark has an x and y coordinate
    output_size = 128
    hidden_layers = 512
    numel = 1024
    num_workers = 8
    pin_memory = True
    checkpoint_path = os.path.join(get_dir('data/models'), 'landmarks_to_style.pth')
    model_save_path = get_dir('data/models')
    style_generator_ckpt_path = os.path.join(get_dir('StyleCariGAN/checkpoint/StyleCariGAN'), '001000.pt')
    cari_attribute_ckpt_path = os.path.join(get_dir('StyleCariGAN/checkpoint/StyleCariGAN'), 'cari_resnet.pth')
    input_path = get_dir('data/input')
    output_path = get_dir('data/gan_images')
    dataset_path = get_dir('data/300W_F')
    log_path = get_dir('data/logs')