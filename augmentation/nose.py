# nose.py

import numpy as np
import cv2
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from landmarking.load import load_feature_landmarks
from augmentation.resize_overlay import resize_and_overlay_feature
from utils.img_utils import multi_res_blend, poisson_blend


def resize_nose(img, facial_features, image_id, feature_to_int, scale_factor):
    '''
    This function is responsible for resizing the nose.
    Gets the coordinates from the .npy file, and finds the feature named 'nose'
    returns the resized nose, with a margin factor to capture the nostrils
    region is overlaid on the image.
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
    This function creates a mask where the area around the nose is white (255), to indicate the ROI. 
    The rest of the mask is black, it can then be used in the blending.
    The mask uses the land mark points, and margin to define the region of the mask. 
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
    mask = np.zeros_like(img)
    x_min, y_min = np.min(feature_points, axis=0).astype(int)
    x_max, y_max = np.max(feature_points, axis=0).astype(int)
    width_margin = int((x_max - x_min) * width_margin_factor)
    height_margin = int((y_max - y_min) * height_margin_factor)
    x_min = max(x_min - width_margin, 0)
    y_min = max(y_min - height_margin, 0)
    x_max = min(x_max + width_margin, img.shape[1])
    y_max = min(y_max + height_margin, img.shape[0])
    mask[y_min:y_max, x_min:x_max] = 255
    
    return mask

def multiply_nose_mask(nose_mask1, nose_mask2, img, original_img):
    # Convert the masks to float32 and normalize them to the range [0, 1]
    nose_mask1 = nose_mask1.astype(np.float32) / 255
    nose_mask2 = nose_mask2.astype(np.float32) / 255

    # Create the inverse masks
    inverse_nose_mask1 = 1 - nose_mask1
    inverse_nose_mask2 = 1 - nose_mask2

    # Multiply the image with the masks and the inverse masks
    img1 = cv2.multiply(img, nose_mask1[:, :, None])
    img2 = cv2.multiply(img, nose_mask2[:, :, None])
    original_img1 = cv2.multiply(original_img, inverse_nose_mask1[:, :, None])
    original_img2 = cv2.multiply(original_img, inverse_nose_mask2[:, :, None])

    # Add the images to create the final result
    result = cv2.add(img1, original_img1)
    result = cv2.add(result, img2)
    result = cv2.add(result, original_img2)

    return result