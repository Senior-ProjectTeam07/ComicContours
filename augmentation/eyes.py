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
    eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
    return resize_and_overlay_feature(img, eye_landmarks, scale_factor, width_margin_factor=0.25,
                                      height_margin_factor=0.4)

def create_eye_mask(eye_landmarks1, eye_landmarks2, img):
    '''
    This function creates a mask for the eyes based on the provided eye landmarks.
    The area around the eyes in the mask is white (indicating the region of interest), while the rest of the mask is black.
    This mask can then be used in blending operations to isolate the eyes.
    The mask is created by filling polygons defined by the eye landmarks with white color.
    A close operation is then applied to the mask to improve its quality.
    '''
    # Create an empty mask
    mask = np.zeros(img.shape, dtype=np.float32)
    # Ensure the eye landmarks are 2D
    if len(eye_landmarks1.shape) < 2:
        eye_landmarks1 = eye_landmarks1.reshape(-1, 2)
    if len(eye_landmarks2.shape) < 2:
        eye_landmarks2 = eye_landmarks2.reshape(-1, 2)
    # Fill polygons defined by the eye landmarks with white color
    cv2.fillConvexPoly(mask, np.int32(eye_landmarks1), (1.0, 1.0, 1.0))
    cv2.fillConvexPoly(mask, np.int32(eye_landmarks2), (1.0, 1.0, 1.0))
    # Convert the mask to uint8
    mask = 255*np.uint8(mask)

    # Apply close operation to improve mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

def multiply_eye_mask(mask, inverse_mask, eye, face):
    '''
    This function applies the mask and its inverse to the eye and face images respectively.
    The mask is applied to the eye image to isolate the eyes, and the inverse mask is applied to the face image to isolate the rest of the face.
    The two images are then added together to create the final result.
    This allows the eyes to be highlighted in the final image, while the rest of the face is still visible.
    '''
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