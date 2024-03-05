# nose.py

import numpy as np
import cv2
import sys
import os

# Get the current directory and parent directory for importing modules
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

# Import necessary modules
from landmarking.load import load_feature_landmarks
from augmentation.resize_overlay import resize_and_overlay_feature
from utils.img_utils import multi_res_blend, poisson_blend


def resize_nose(img, facial_features, image_id, feature_to_int, scale_factor):
    '''
    This function resizes the nose in the image based on the provided scale factor.
    It first loads the nose landmarks from the facial features using the provided image ID.
    Then, it resizes and overlays the nose region on the image, adding a margin to capture the nostrils.
    The width margin factor and height margin factor are set to 0.6 and 0.7 respectively to ensure the nostrils are included.
    '''
    # Validate input parameters
    if img is None or img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Input image must be a 3D array with 3 channels.")
    if not isinstance(facial_features, np.ndarray) or facial_features.size == 0:
        raise ValueError("Facial features data must be a non-empty numpy array.")
    if not isinstance(scale_factor, (int, float)):
        raise ValueError("Scale factor must be a number.")
    if scale_factor <= 0 or scale_factor > 3:
        raise ValueError("Scale factor must be in the range (0, 3].")
    
    try:
        nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')
        if nose_landmarks.size == 0:
            raise ValueError("No nose landmarks found for the given image ID.")
    except Exception as e:
        raise ValueError(f"Error loading nose landmarks: {e}")

    try:
        return resize_and_overlay_feature(img, nose_landmarks, scale_factor, width_margin_factor=0.6, height_margin_factor=0.7)
    except Exception as e:
        raise ValueError(f"Error resizing and overlaying nose feature: {e}")

def create_nose_mask(img, feature_points, width_margin_factor, height_margin_factor):
    '''
    This function creates a mask for the nose based on the provided feature points.
    The area around the nose in the mask is white (indicating the region of interest), while the rest of the mask is black.
    This mask can then be used in blending operations to isolate the nose.
    The mask is created by filling a rectangle defined by the feature points and margins with white color.
    '''
    # Check if img is a 3D array with 3 channels
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Input image must be a 3D array with 3 channels.")
    # Check if feature_points is a 2D array with 2 columns
    if feature_points.ndim != 2 or feature_points.shape[1] != 2:
        raise ValueError("Feature points must be a 2D array with 2 columns.")
    # Check if width_margin_factor and height_margin_factor are numbers between 0 and 1
    if not isinstance(width_margin_factor, (int, float)) or not isinstance(height_margin_factor, (int, float)):
        raise ValueError("Width and height margin factors must be numbers.")
    if not (0 <= width_margin_factor <= 1) or not (0 <= height_margin_factor <= 1):
        raise ValueError("Width and height margin factors must be numbers between 0 and 1.")
    # Create the mask
    # Create an empty mask
    mask = np.zeros_like(img)
    # Calculate the minimum and maximum coordinates of the feature points
    x_min, y_min = np.min(feature_points, axis=0).astype(int)
    x_max, y_max = np.max(feature_points, axis=0).astype(int)
    # Calculate the width and height margins
    width_margin = int((x_max - x_min) * width_margin_factor)
    height_margin = int((y_max - y_min) * height_margin_factor)
    # Adjust the minimum and maximum coordinates with the margins
    x_min = max(x_min - width_margin, 0)
    y_min = max(y_min - height_margin, 0)
    x_max = min(x_max + width_margin, img.shape[1])
    y_max = min(y_max + height_margin, img.shape[0])
    # Fill the rectangle defined by the adjusted coordinates with white color
    mask[y_min:y_max, x_min:x_max] = 255
    return mask

def multiply_nose_mask(nose_mask1, nose_mask2, img, original_img):
    '''
    This function applies the nose masks and their inverses to the image and original image respectively.
    The nose masks are applied to the image to isolate the noses, and the inverse masks are applied to the original image to isolate the rest of the face.
    The four images are then added together to create the final result.
    This allows the noses to be highlighted in the final image, while the rest of the face is still visible.
    '''
    # Convert the masks to float32 and normalize them to the range [0, 1]
    nose_mask1 = nose_mask1.astype(np.float32) / 255
    nose_mask2 = nose_mask2.astype(np.float32) / 255
    # Create the inverse masks
    inverse_nose_mask1 = 1 - nose_mask1
    inverse_nose_mask2 = 1 - nose_mask2
    # Multiply the image and original image by the masks and inverse masks respectively
    img1 = cv2.multiply(img, nose_mask1[:, :, None])
    img2 = cv2.multiply(img, nose_mask2[:, :, None])
    original_img1 = cv2.multiply(original_img, inverse_nose_mask1[:, :, None])
    original_img2 = cv2.multiply(original_img, inverse_nose_mask2[:, :, None])
    # Add the four images together
    result = cv2.add(img1, original_img1)
    result = cv2.add(result, img2)
    result = cv2.add(result, original_img2)
    return result