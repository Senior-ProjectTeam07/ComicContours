# eyes.py 

import cv2
import numpy as np
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

def resize_eyes(img, facial_features, image_id, feature_to_int, scale_factor):
    '''
    This function resizes the eyes in the image based on the provided scale factor.
    It first loads the eye landmarks from the facial features using the provided image ID.
    Then, it resizes and overlays the eye region on the image, adding a margin to capture the eyelashes.
    The width margin factor and height margin factor are set to 0.25 and 0.4 respectively to ensure the eyelashes are included.
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
        right_eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'Right_Eye')
        left_eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'Left_Eye')
        if right_eye_landmarks.size == 0 or left_eye_landmarks.size == 0:
            raise ValueError("No eye landmarks found for the given image ID.")
    except Exception as e:
        raise ValueError(f"Error loading eye landmarks: {e}")

    try:
        img = resize_and_overlay_feature(img, right_eye_landmarks, scale_factor, width_margin_factor=0.25, height_margin_factor=0.4)
        img = resize_and_overlay_feature(img, left_eye_landmarks, scale_factor, width_margin_factor=0.25, height_margin_factor=0.4)
        return img
    except Exception as e:
        raise ValueError(f"Error resizing and overlaying eye feature: {e}")

def create_eye_mask(eye_landmarks, img):
    '''
    This function creates a mask for the eyes based on the provided eye landmarks.
    The area around the eyes in the mask is white (indicating the region of interest), while the rest of the mask is black.
    This mask can then be used in blending operations to isolate the eyes.
    The mask is created by filling polygons defined by the eye landmarks with white color.
    A close operation is then applied to the mask to improve its quality.
    '''
    # Ensure the eye landmarks are not empty
    if eye_landmarks.size == 0:
        raise ValueError("Eye landmarks are empty.")
    # Ensure the eye landmarks are 2D
    if len(eye_landmarks.shape) != 2:
        raise ValueError("eye_landmarks must be a 2D array of shape (n, 2)")
    # Ensure the eye landmarks contain only non-negative integers
    if np.any(eye_landmarks < 0) or not np.issubdtype(eye_landmarks.dtype, np.integer):
        raise ValueError("eye_landmarks must contain only non-negative integers.")
    # Ensure the eye landmarks are within the image boundaries
    if np.any(eye_landmarks < 0) or np.any(eye_landmarks[:, 0] >= img.shape[1]) or np.any(eye_landmarks[:, 1] >= img.shape[0]):
        raise ValueError("Eye landmarks are outside the image boundaries")
    
    # Create an empty mask
    mask = np.zeros(img.shape, dtype=np.float32)

    # Convert the landmarks to a 2D array of integers
    eye_landmarks = np.array(eye_landmarks, dtype=np.int32).reshape((-1, 2))

    # Fill the polygon defined by the eye landmarks with white color
    cv2.fillConvexPoly(mask, eye_landmarks, (1.0, 1.0, 1.0))

    # Convert the mask to uint8
    mask = 255*np.uint8(mask)

    # Apply close operation to improve mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def multiply_eye_mask(eye_landmarks, eye, face):
    '''
    This function applies the mask and its inverse to the eye and face images respectively.
    The mask is applied to the eye image to isolate the eyes, and the inverse mask is applied to the face image to isolate the rest of the face.
    The two images are then added together to create the final result.
    This allows the eyes to be highlighted in the final image, while the rest of the face is still visible.
    '''
    # Create a mask for the eye
    mask = create_eye_mask(eye_landmarks, face)

    # Create the inverse mask
    inverse_mask = 1 - mask

    # Ensure mask and inverse_mask have the same type as eye and face
    mask = mask.astype(eye.dtype)
    inverse_mask = inverse_mask.astype(face.dtype)

    # Multiply the eye and face images by the mask and inverse mask respectively
    just_eye = cv2.multiply(mask, eye)
    just_face = cv2.multiply(inverse_mask, face)

    # Ensure just_eye and just_face have the same type
    just_eye = just_eye.astype(just_face.dtype)

    # Add the eye and face images together
    result = cv2.add(just_face, just_eye)

    return result