# image_utils.py

import numpy as np
import cv2
from scipy.sparse import lil_matrix
from skimage import img_as_float
from scipy.sparse.linalg import spsolve
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

def histogram_matching_luminance(source, template):
    """
    Match the histogram of the source image to that of the template image using only the luminance channel.
    """
    source_ycbcr = rgb_to_ycbcr(source)
    template_ycbcr = rgb_to_ycbcr(template)

    # Apply histogram equalization to the Y channel of the source image
    source_y_equalized = cv2.equalizeHist(source_ycbcr[:, :, 0])
    
    # Apply histogram equalization to the Y channel of the template image
    template_y_equalized = cv2.equalizeHist(template_ycbcr[:, :, 0])
    
    # Perform histogram matching
    matched_y = cv2.matchTemplate(source_y_equalized, template_y_equalized, method=cv2.TM_CCOEFF_NORMED)
    
    # Replace the Y channel of the source image with the matched Y channel
    source_ycbcr[:, :, 0] = matched_y

    # Convert back to RGB
    matched_rgb = ycbcr_to_rgb(source_ycbcr)

    return matched_rgb

def alpha_blend(img1, img2, mask):
    """
    Blend two images using a mask and its inverse.
    :param img1: First image, expected to be a numpy array.
    :param img2: Second image, should be the same size and type as img1.
    :param mask: Blending mask, can be 1 or 3 channels. If 3 channels, it will be converted to grayscale.
    :return: Blended image as a numpy array.
    """
    assert img1.shape[:2] == img2.shape[:2] == mask.shape[:2], "Images and mask must have the same width and height"
    if mask.dtype == np.float64:  # If mask is 64-bit floating point
        mask = mask.astype(np.float32)  # Convert mask to 32-bit floating point
    if mask.ndim == 3 and mask.shape[2] == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask = mask.astype(np.float32) / 255.0
    inv_mask = 1.0 - mask
    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)
    # Add an extra dimension to mask if necessary
    if img1.ndim > mask.ndim:
        mask = np.expand_dims(mask, axis=-1)
        inv_mask = np.expand_dims(inv_mask, axis=-1)
    # Repeat the mask along the channel dimension if necessary
    if img1.shape != mask.shape:
        mask = np.repeat(mask, img1.shape[2], axis=2)
        inv_mask = np.repeat(inv_mask, img1.shape[2], axis=2)
    try:
        blended = cv2.multiply(img1, mask) + cv2.multiply(img2, inv_mask)
    except cv2.error as e:
        print(f"img1.shape: {img1.shape}, mask.shape: {mask.shape}")
        print(f"img2.shape: {img2.shape}, inv_mask.shape: {inv_mask.shape}")
        raise e
    # Clip values to ensure they are within [0, 255] range before casting to uint8
    blended_clipped = np.clip(blended, 0, 255)
    
    return blended_clipped.astype(np.uint8)


def multi_res_blend(mask, source, target):
    # Generate Gaussian pyramid for source
    gp_source = [source]
    for i in range(6):
        source = cv2.pyrDown(source)
        gp_source.append(source)

    # Generate Gaussian pyramid for target
    gp_target = [target]
    for i in range(6):
        target = cv2.pyrDown(target)
        gp_target.append(target)

    # Generate Gaussian pyramid for mask
    gp_mask = [mask]
    for src, tgt in zip(gp_source, gp_target):
        # mask = cv2.resize(mask, (src.shape[1], src.shape[0]))
        mask = cv2.pyrDown(mask)
        gp_mask.append(mask)

    # Generate Laplacian Pyramid for source
    lp_source = [gp_source[5]]
    for i in range(5, 0, -1):
        size = (gp_source[i - 1].shape[1], gp_source[i - 1].shape[0])
        ge = cv2.pyrUp(gp_source[i], dstsize=size)
        ge = cv2.resize(ge, size)
        lp = cv2.subtract(gp_source[i - 1], ge)
        lp = cv2.resize(lp, size)
        lp_source.append(lp)

    # Generate Laplacian Pyramid for target
    lp_target = [gp_target[5]]
    for i in range(5, 0, -1):
        size = (gp_target[i - 1].shape[1], gp_target[i - 1].shape[0])
        ge = cv2.pyrUp(gp_target[i], dstsize=size)
        ge = cv2.resize(ge, size)
        lp = cv2.subtract(gp_target[i - 1], ge)
        lp = cv2.resize(lp, size)
        lp_target.append(lp)

    # Add left and right halves of images in each level
    LS = [] 
    for lsrc, ltar, gmask in zip(lp_source, lp_target, gp_mask):
        print(lsrc.shape)
        print(gmask.shape)
        print(ltar.shape)
        ls = lsrc * gmask + ltar * (1.0 - gmask)
        LS.append(ls)

    # now reconstruct
    ls_ = LS[0]
    for i in range(1, 6):
        size = (LS[i].shape[1], LS[i].shape[0])
        ls_ = cv2.pyrUp(ls_, dstsize=size)
        ls_ = cv2.add(ls_, LS[i])

    return ls_

def poisson_blend(mask, source, target, offset):
    # Ensure mask is float type and in the range 0-1
    mask = img_as_float(mask)

    # Define build_matrix function
    def build_matrix(indices):
        kernel = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        size = len(indices)
        A = lil_matrix((size, size))
        for i in range(size):
            A[i, i] = 4
            if i % mask.shape[1] > 0: A[i, i - 1] = -1  # left
            if (i + 1) % mask.shape[1] > 0 and i + 1 < size: A[i, i + 1] = -1  # right
            if i // mask.shape[1] > 0: A[i, i - mask.shape[1]] = -1  # up
            if i // mask.shape[1] < mask.shape[0] - 1 and i + mask.shape[1] < size: A[i, i + mask.shape[1]] = -1  # down
        return A

    def build_b(source, target, mask, indices):
        size = len(indices)
        b = np.zeros(size)
        num_layers = source.shape[2] if source.ndim > 2 else 1
        for color in range(num_layers):
            for i, index in enumerate(indices):
                y, x = np.unravel_index(index[0], mask.shape[:2])
                b[i] = 4 * source[y, x, color] if source.ndim > 2 else 4 * source[y, x]
                if x > 0: b[i] -= source[y, x - 1, color] + target[y, x - 1, color] * (1 - mask[y, x - 1]) if source.ndim > 2 else source[y, x - 1] + target[y, x - 1] * (1 - mask[y, x - 1])
                if x < mask.shape[1] - 1: b[i] -= source[y, x + 1, color] + target[y, x + 1, color] * (1 - mask[y, x + 1]) if source.ndim > 2 else source[y, x + 1] + target[y, x + 1] * (1 - mask[y, x + 1])
                if y > 0: b[i] -= source[y - 1, x, color] + target[y - 1, x, color] * (1 - mask[y - 1, x]) if source.ndim > 2 else source[y - 1, x] + target[y - 1, x] * (1 - mask[y - 1, x])
                if y < mask.shape[0] - 1: b[i] -= source[y + 1, x, color] + target[y + 1, x, color] * (1 - mask[y + 1, x]) if source.ndim > 2 else source[y + 1, x] + target[y + 1, x] * (1 - mask[y + 1, x])
        return b

    # Compute regions to be blended
    region_source = (
            max(-offset[0], 0),
            max(-offset[1], 0),
            min(target.shape[0]-offset[0], source.shape[0]),
            min(target.shape[1]-offset[1], source.shape[1]))
    region_target = (
            max(offset[0], 0),
            max(offset[1], 0),
            min(target.shape[0], source.shape[0]+offset[0]),
            min(target.shape[1], source.shape[1]+offset[1]))

    # Clip and normalize mask image
    mask = mask[region_source[0]:region_source[2], region_source[1]:region_source[3]]
    mask[mask!=0] = 1

    # Create coefficient matrix
    indices = np.argwhere(mask)
    A = build_matrix(indices)

    # Convert A to CSR format
    A = A.tocsr()

    # for each layer (ex. RGB)
    for num_layer in range(source.shape[2]):
        # get subimages
        t = target[region_target[0]:region_target[2], region_target[1]:region_target[3], num_layer]
        s = source[region_source[0]:region_source[2], region_source[1]:region_source[3], num_layer]

        # create b
        b = build_b(s, t, mask, indices)

        # solve Ax = b
        x = spsolve(A, b)

        # assign x to target image
        x = np.clip(x, 0, 255)  # Clip to the range 0-255
        x = np.reshape(x, (len(indices), 1))
        indices_x = np.concatenate((indices, x), axis=1)
        for index in indices_x:
            target[int(index[0] + offset[0]), int(index[1] + offset[1]), num_layer] = index[2]

    return target