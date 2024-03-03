# image_utils.py

import numpy as np
import cv2
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

def rgb_to_ycbcr(image):
    """Converts an RGB image to YCbCr color space."""
    if image.size == 0:
        raise ValueError("Input image cannot be empty.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Input must be a three-dimensional array with three channels.")
    xform = np.array([[.299, .587, .114], [-.1687, -.3313, .5], [.5, -.4187, -.0813]])
    ycbcr = image.dot(xform.T)
    ycbcr[:,:,[1,2]] += 128
    
    return np.clip(ycbcr, 0, 255).astype(np.uint8)

def ycbcr_to_rgb(image):
    """Converts a YCbCr image back to RGB color space."""
    if not (image.ndim == 3 and image.shape[2] == 3):
        raise ValueError("Input must be a YCbCr image.")
    
    image = image.astype(np.float32) if image.dtype != np.float32 else image
    Y, Cb, Cr = image[:, :, 0], image[:, :, 1] - 128, image[:, :, 2] - 128
    R = Y + 1.402 * Cr
    G = Y - 0.344136 * Cb - 0.714136 * Cr
    B = Y + 1.772 * Cb
    RGB = np.stack((R, G, B), axis=-1)

    return np.clip(RGB, 0, 255).astype(np.uint8)

def dynamic_range_compression(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    image = image.astype(np.float32) if image.dtype != np.float32 else image
    if len(image.shape) == 3 and image.shape[2] == 3:
        ycbcr_image = rgb_to_ycbcr(image)
        y_channel = ycbcr_image[:, :, 0]
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        ycbcr_image[:, :, 0] = clahe.apply(y_channel)
        return ycbcr_to_rgb(ycbcr_image)
    elif len(image.shape) == 2:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)
    else:
        raise ValueError("Unsupported image format.")
    
def equalize_grayscale(image):
    """Applies histogram equalization to a grayscale image."""
    hist, bins = np.histogram(image.flatten(), bins=256, range=[0, 256])
    cdf = hist.cumsum()
    cdf_masked = np.ma.masked_equal(cdf, 0)
    cdf_masked = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
    cdf = np.ma.filled(cdf_masked, 0).astype('uint8')

    return cdf[image]

def equalize_color(image):
    """Applies histogram equalization to the Y channel of a color image in YCbCr color space."""
    ycbcr_image = rgb_to_ycbcr(image)
    ycbcr_image[:, :, 0] = equalize_grayscale(ycbcr_image[:, :, 0])
    
    return ycbcr_to_rgb(ycbcr_image)

def match_histograms(source, template):
    """Adjusts the pixel values of a source image to match the histogram of a template image."""
    if source is None or template is None:
        raise ValueError("Source and template images cannot be None.")
    if source.size == 0 or template.size == 0:
        raise ValueError("Source and template images cannot be empty.")
    if source.shape[:2] != template.shape[:2]:
        raise ValueError("Source and template images must have the same dimensions.")

    source_processed = equalize_color(source) if source.ndim == 3 else equalize_grayscale(source)
    template_processed = equalize_color(template) if template.ndim == 3 else equalize_grayscale(template)
    source_lab = cv2.cvtColor(source_processed, cv2.COLOR_BGR2Lab)
    template_lab = cv2.cvtColor(template_processed, cv2.COLOR_BGR2Lab)
    source_lab = dynamic_range_compression(source_lab)
    template_lab = dynamic_range_compression(template_lab)

    for i in range(3):
        source_hist = np.histogram(source_lab[:, :, i], bins=256)[0]
        template_hist = np.histogram(template_lab[:, :, i], bins=256)[0]
        source_cdf = np.cumsum(source_hist).astype(float)
        template_cdf = np.cumsum(template_hist).astype(float)
        source_cdf_normalized = source_cdf / source_cdf[-1]
        template_cdf_normalized = template_cdf / template_cdf[-1]
        mapping = np.interp(source_cdf_normalized, template_cdf_normalized, np.arange(256))
        source_lab[:, :, i] = np.interp(source_lab[:, :, i].flatten(), np.arange(256), mapping).reshape(source_lab[:, :, i].shape)

    matched_bgr = cv2.cvtColor(source_lab, cv2.COLOR_Lab2BGR)
    return matched_bgr if source.ndim == 3 else cv2.cvtColor(matched_bgr, cv2.COLOR_BGR2GRAY)

def alpha_blend(img1, img2, mask):
    """
    Blend two images using a mask.
    This function has been optimized for efficiency while maintaining edge case handling.
    :param img1: First image, expected to be a numpy array.
    :param img2: Second image, should be the same size and type as img1.
    :param mask: Blending mask, can be 1 or 3 channels. If 3 channels, it will be converted to grayscale.
    :return: Blended image as a numpy array.
    """
    if mask.dtype == np.float64:  # If mask is 64-bit floating point
        mask = mask.astype(np.float32)  # Convert mask to 32-bit floating point
    if mask.ndim == 3 and mask.shape[2] == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask = mask.astype(np.float32) / 255.0
    img1 = img1.astype(np.float32) / 255.0
    img2 = img2.astype(np.float32) / 255.0
    # Add an extra dimension to mask if necessary
    if mask.ndim != img1.ndim:
        mask = np.expand_dims(mask, axis=-1)
    blended = img1 * mask + img2 * (1 - mask)
    # Clip values to ensure they are within [0, 255] range before casting to uint8
    blended_clipped = np.clip(blended * 255, 0, 255)
    
    return blended_clipped.astype(np.uint8)