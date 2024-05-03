# test.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import math
import numpy as np
import argparse
from PIL import Image
import torch
from torch import nn
from torchvision import transforms, utils
from torchvision.transforms import functional as F

from invert import *
from exaggeration_model import StyleCariGAN 

from align import ImageAlign



def invert_and_generate(generator, perceptual, image, device, args):
    # Assuming this is a placeholder function to handle inversion logic
    # Normally, this would perform operations similar to an encoder, projecting image features to latent space
    # For this example, let's return a dummy tensor for wp and noise
    wp = torch.randn(1, 512, device=device)
    noise = [torch.randn(1, 512, 1, 1, device=device) for _ in range(10)]
    return {'wp': wp, 'noise': noise}

@torch.no_grad()
def generate(generator, truncation, truncation_latent, wp, noise, styles, device, output_dir, img_name):
    os.makedirs(output_dir, exist_ok=True)
    phi = [1 - args.exaggeration_factor] * 4
    img = generator(wp, [styles[0]], noise=noise, input_is_w_plus=True,
                    truncation=truncation, truncation_latent=truncation_latent,
                    mode='p2c', phi=phi)
    utils.save_image(img['result'], os.path.join(output_dir, f'{img_name}.png'),
                     normalize=True, range=(-1, 1))

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Generate caricatures from user input images")
    parser.add_argument('--ckpt', type=str, required=True, help='path to checkpoint')
    parser.add_argument('--input_dir', type=str, required=True, help='directory with input images')
    parser.add_argument('--output_dir', type=str, required=True, help='directory to save generated caricatures')
    parser.add_argument('--size', type=int, required=True, help='input and output image size (e.g., 256 for 256x256 pixels)')
    parser.add_argument('--latent', type=int, default=512, help='dimensionality of the latent space')
    parser.add_argument('--n_mlp', type=int, default=8, help='number of layers in the mapping network')
    parser.add_argument('--channel_multiplier', type=int, default=2, help='multiplier for the number of channels in convolutional layers')
    parser.add_argument('--exaggeration_factor', type=float, default=1.0, help='exaggeration factor, 0 to 1')
    parser.add_argument('--truncation', type=float, default=1.0, help='truncation for the latent space')

    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else 'cpu'
    align = ImageAlign()
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])

    # Initialize StyleCariGAN
    g_ema = StyleCariGAN(args.size, args.latent, args.n_mlp, channel_multiplier=args.channel_multiplier).to(device)
    g_ema.load_state_dict(torch.load(args.ckpt)['g_ema'], strict=False)
    g_ema.eval()

    # Load or generate styles
    if os.path.exists(args.predefined_style):
        styles = torch.from_numpy(np.load(args.predefined_style)).to(device)
    else:
        # Example fallback: Generate random styles if not provided
        styles = torch.randn([10, args.latent], device=device)  # 10 random style vectors

    mean_latent = g_ema.photo_generator.mean_latent(args.truncation_mean) if args.truncation < 1 else None

    # Inversion and generation loop
    for img_file in os.listdir(args.input_dir):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(args.input_dir, img_file)
            img = Image.open(full_path).convert('RGB')
            img_tensor = transform(img).unsqueeze(0).to(device)

            # Perform inversion to get latent code (wp) and noise
            wp, noise = invert(g_ema, img_tensor, device, args)

            # Generate caricature using the obtained latent code and noise
            generate(g_ema, args.truncation, mean_latent, wp, noise, styles, device, args.output_dir, img_file.split('.')[0])

    print("Finished generating caricatures.")