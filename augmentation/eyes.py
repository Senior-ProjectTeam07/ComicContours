# eyes.py 

import cv2
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from landmarking.load import load_feature_landmarks
from augmentation.resize_overlay import resize_and_overlay_feature
from utils.img_utils import multi_res_blend, poisson_blend

def resize_eyes(img, facial_features, image_id, feature_to_int, scale_factor):
    '''
    Similar to resize nose, but for eyes.
    returns the resized eyes, with margin to capture eye lashes.
    region is overlaid on the image.
    '''
    eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
    return resize_and_overlay_feature(img, eye_landmarks, scale_factor, width_margin_factor=0.25,
                                      height_margin_factor=0.4)

def resize_eyes(img, facial_features, image_id, feature_to_int, scale_factor):
    try:
        eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
        if eye_landmarks.size == 0:
            raise ValueError("No eye landmarks found for the given image ID.")
    except Exception as e:
        raise ValueError(f"Error loading eye landmarks: {e}")

    try:
        return resize_and_overlay_feature(img, eye_landmarks, scale_factor, width_margin_factor=0.6, height_margin_factor=0.7)
    except Exception as e:
        raise ValueError(f"Error resizing and overlaying eye feature: {e}")
    
def create_eye_mask(eye_landmarks1, eye_landmarks2, img):
    '''
    This function creates a mask where the area around the mask is white, to indicate the ROI. 
    The rest of the mask is black, it can then be used in the blending.
    The mask uses the land mark points to define the region of the mask. 
    '''
    # mask 1, makes mask for reduced eye
    mask = np.zeros(img.shape, dtype=np.float32)
    if len(eye_landmarks1.shape) < 2:
        eye_landmarks1 = eye_landmarks1.reshape(-1, 2)
    if len(eye_landmarks2.shape) < 2:
        eye_landmarks2 = eye_landmarks2.reshape(-1, 2)
    cv2.fillConvexPoly(mask, np.int32(eye_landmarks1), (1.0, 1.0, 1.0))
    cv2.fillConvexPoly(mask, np.int32(eye_landmarks2), (1.0, 1.0, 1.0))
    mask = 255*np.uint8(mask)

    # Apply close operation to improve mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask

def multiply_eye_mask(mask, inverse_mask, eye, face):
    '''
    This function puts the image in the mask and puts an image in the inverse mask. For mask it puts a reduced image 
    of the eyes in the mask. While for mask2 it puts a blended image in the mask2 and 
    the normal image in each ones inverse mask.
    '''
    # Ensure mask and inverse_mask have the same type as eye and face
    mask = mask.astype(eye.dtype)
    inverse_mask = inverse_mask.astype(face.dtype)
    # Perform blending
    just_eye = cv2.multiply(mask, eye)
    just_face = cv2.multiply(inverse_mask, face)
    # Ensure just_eye and just_face have the same type
    just_eye = just_eye.astype(just_face.dtype)
    # Add face and eye
    result = cv2.add(just_face, just_eye)
    return result

'''
def multiply_eye_mask(mask, inverse_mask, eye, face):

    This function puts the image in the mask and puts an image in the inverse mask. For mask it puts a reduced image 
    of the eyes in the mask. While for mask2 it puts a blended image in the mask2 and 
    the normal image in each ones inverse mask.

    # Ensure mask and inverse_mask have the same type as eye and face
    mask = mask.astype(eye.dtype)
    inverse_mask = inverse_mask.astype(face.dtype)
    # Perform blending
    just_eye = cv2.multiply(mask, eye)
    just_face = cv2.multiply(inverse_mask, face)
    # Ensure just_eye and just_face have the same type
    just_eye = just_eye.astype(just_face.dtype)
    result = just_face + just_eye  # Add face and eye
    return result



def multiply_eye_mask(mask, inverse_mask, eye, face):
    # Multiply eyes and face by the mask
    just_eye = cv2.multiply(mask, eye)
    just_face = cv2.multiply(inverse_mask, face)
    result = just_face + just_eye  # Add face and eye
    return result
'''