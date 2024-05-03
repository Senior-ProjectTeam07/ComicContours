# generate.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import math
import torch
import argparse
import warnings
from torch import nn
from torchvision import transforms, utils
from torchvision.transforms.functional import to_tensor
import numpy as np
import logging
from PIL import Image
from torchvision import transforms
from StyleCariGAN.model import Generator  # Import StyleCariGAN generator
from StyleCariGAN.invert import *  # Invert function
from StyleCariGAN.exaggeration_model import StyleCariGAN  # StyleCariGAN class
from StyleCariGAN.align import ImageAlign
from landmarks_to_style.data_loader import get_dataloaders
from landmarks_to_style.model_loader import load_stylecarigan, load_landmarkstostyles
from landmarks_to_style.config import Config
from landmarks_to_style.generate_styles import generate_style_vectors
from utils.file_utils import get_dir

# Improve generation speed by switching to benchmark mode
torch.backends.cudnn.benchmark = True

# Suppress less critical warnings to streamline output
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.checkpoint")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data._utils.pin_memory")

# Check and prepare CUDA device for operations
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == 'cuda':
    try:
        torch.cuda.synchronize()  # Ensure all CUDA operations are synchronized
        torch.cuda.empty_cache()  # Clear cached memory to minimize memory overhead
    except RuntimeError as e:
        logging.error(f"Failed to initialize CUDA: {e}")

@torch.no_grad()
def generate(
    generator, truncation, truncation_latent, inversion_file, styles, device
):
    try:
        if os.path.exists(os.path.splitext(inversion_file)[0]+'_style.pt'):
            indices = torch.load(os.path.splitext(inversion_file)[0]+'_style.pt')
        else:
            indices = range(styles.shape[0])
        if os.path.exists(inversion_file) and os.path.getsize(inversion_file) > 0:
            inversion_file = torch.load(inversion_file)
        else:
            print(f"File {inversion_file} does not exist or is empty.")
            return
        wp = inversion_file['wp'].to(device).unsqueeze(0)
        noise = [n.to(device) for n in inversion_file['noise']]
        os.makedirs(args.current_output_dir, exist_ok=True)

        phi = [1-args.exaggeration_factor] * 4
        for i in indices:
            img = generator(wp, [styles[i]], noise=noise, input_is_w_plus=True, \
                    truncation=truncation, truncation_latent=truncation_latent,\
                    mode='p2c', phi = phi)

            # Normalize the image to the range (-1, 1)
            img['result'] = (img['result'] + 1) / 2

            utils.save_image(
                img['result'],
                os.path.join(args.output_dir, f'{args.image_name}_gan'),
                nrow=1,
                normalize=True,
            )
    except Exception as e:
        print(f"An error occurred while processing {inversion_file}: {e}")

'''
def generate_caricature_test(args):
   
    # Initialize data loader
    dataloader = get_dataloaders(
        Config.input_path, Config.train_batch_size, Config.val_batch_size,
        Config.num_workers, Config.pin_memory, single_set=True
    )

    # Generate the style vector from landmarks
    landmarks_to_style = load_landmarkstostyles(
            Config.checkpoint_path, device, Config.input_size, Config.output_size,
            Config.hidden_layers, Config.numel
        ).to(device)
    landmarks_to_style.eval()

    style_vector = generate_style_vectors(landmarks_to_style, dataloader, device).to(device)

    # Clear unnecessary tensors from memory to maintain a low memory footprint.
    del landmarks_to_style
    torch.cuda.empty_cache()  # Helps in avoiding CUDA out of memory errors.

    # Load StyleCariGAN
    g_ema = load_stylecarigan(
            Config.style_generator_ckpt_path, device, Config.generate_size, 
            Config.generate_style_dim, Config.n_mlp, Config.channel_multiplier
        ).to(device)
    g_ema.eval()

    # Generate caricature using StyleCariGAN and the style vector
    generate(g_ema, args.truncation, None, [style_vector], device)
'''
    
def main():
    parser = argparse.ArgumentParser(description="Generate caricatures from user input images")

    parser.add_argument("--truncation", type=float, default=1, help="truncation factor")
    parser.add_argument("--truncation_mean", type=int, default=4096, help="number of samples to calculate mean for truncation")
    parser.add_argument("--size", type=int, default=256, help="image sizes for generator")
    parser.add_argument('--ckpt', type=str, default=os.path.join(get_dir('StyleCariGAN/checkpoint/StyleCariGAN'), '001000.pt'), help='path to checkpoint')
    parser.add_argument('--input_dir', type=str, default=get_dir('data/original_images'), help='directory with input inverted .pt files or input images to invert')
    parser.add_argument('--output_dir', type=str, default=get_dir('data/gan_images'), help='directory to save generated caricatures')
    parser.add_argument('--predefined_style', type=str, default="/home/jojo/OneDrive/UNR/CS426/ComicContours/StyleCariGAN/style_palette/style_palette_27.npy", help='pre-selected style z-vector file')
    parser.add_argument('--exaggeration_factor', type=float, default=1.0, help='exaggeration factor, 0 to 1')
    parser.add_argument('--invert_images', action='store_true', default=True, help='invert images in sample folder to generate caricature from them')

    # used if args.invert_images is true
    parser.add_argument("--w_iterations", type=int, default=250)
    parser.add_argument("--wp_iterations", type=int, default=2000)
    parser.add_argument("--lambda_l2", type=float, default=1)
    parser.add_argument("--lambda_p", type=float, default=1)    
    parser.add_argument("--lambda_noise", type=float, default=1e5)
    parser.add_argument("--wlr", type=float, default=4e-3)
    parser.add_argument("--lr_decay_rate", type=float, default=0.2)
    parser.add_argument("--save", action='store_true')

    args = parser.parse_args()

     # constant
    args.latent = 512
    args.num_layers = 14
    args.n_mlp = 8
    args.channel_multiplier = 2

    styles = torch.from_numpy(np.load(args.predefined_style)).to(device) # shape N * 512
    styles = styles.unsqueeze(1)

    ckpt = torch.load(args.ckpt)
    g_ema = StyleCariGAN(
        args.size, args.latent, args.n_mlp, channel_multiplier=args.channel_multiplier
    ).to(device)
    checkpoint = torch.load(args.ckpt)
    g_ema.load_state_dict(ckpt['g_ema'], strict=False)
    del ckpt

    if args.truncation < 1:
        with torch.no_grad():
            mean_latent = g_ema.photo_generator.mean_latent(args.truncation_mean)
    else:
        mean_latent = None

    if args.invert_images:
        align = ImageAlign()

        perceptual = perceptual_module().to(device)
        perceptual.eval()
        transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True),])

        n=50000
        samples = 256
        w = []
        for _ in range(n//samples):
            sample_z = mixing_noise(samples, args.latent, 0, device=device)
            w.append(g_ema.photo_generator.style(sample_z))
        w = torch.cat(w, dim=0)
        args.mean_w = w.mean(dim=0)

        for fn in os.listdir(args.input_dir):
            if fn.endswith('.png') or fn.endswith('.jpg'):
                if os.path.exists(os.path.join(args.input_dir, fn.split('.')[0]+'.pt')):
                    continue
                args.result_dir = args.input_dir
                args.image_name = fn.split('.')[0]
                args.image = os.path.join(args.input_dir, fn)
                aligned_image = align(args.image)
                if aligned_image is None:
                    print(f"Face not detected in {args.image}, skipping this image.")
                    continue
                photo = transform(aligned_image).unsqueeze(0).to(device)
                args.image_name = args.image.split('/')[-1].split('.')[0]
                invert(g_ema.photo_generator, perceptual, photo, device, args)

    os.makedirs(args.output_dir, exist_ok=True)
    for fn in os.listdir(args.input_dir):
        if fn.endswith('.png') or fn.endswith('.jpg'):
            args.image_name = fn.split('.')[0]
            inversion_file = os.path.join(args.input_dir, args.image_name+'.pt')
            args.current_output_dir = os.path.join(args.output_dir, args.image_name)
            generate(
                g_ema, args.truncation, mean_latent, inversion_file, styles, device
            )
if __name__ == "__main__":
    main()