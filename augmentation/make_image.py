# make_image.py

import cv2
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.eyes import multiply_eye_mask

def prepare_mask(mask):
    if len(mask.shape) == 2:  # mask is grayscale
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Convert grayscale mask to BGR
    inverse_mask = cv2.bitwise_not(mask)  # Calculate inverse mask
    if len(inverse_mask.shape) == 2:  # inverse_mask is grayscale
        inverse_mask = cv2.cvtColor(inverse_mask, cv2.COLOR_GRAY2BGR)  # Convert grayscale inverse_mask to BGR
    mask = mask.astype(float)/255
    inverse_mask = inverse_mask.astype(float)/255
    return mask, inverse_mask

def make_eye_img(img, mask, face_landmarks, eyebrow_landmarks, face_img):
    mask, inverse_mask = prepare_mask(mask)
    img = img.astype(np.uint8)  # Apply color mapping for the eyes
    face_width = face_landmarks[0, 1]
    eyebrow_height = eyebrow_landmarks[3, 1]
    h, w, c = img.shape
    height_reduced = int((h-eyebrow_height)/32)
    width_reduced = int((w-face_width)/8)
    eye = cv2.copyMakeBorder(img, height_reduced, height_reduced*3, width_reduced, width_reduced, cv2.BORDER_CONSTANT)
    eye = cv2.resize(eye, (w, h))
    eye = eye.astype(float)/255
    result = multiply_eye_mask(mask, inverse_mask, eye, face_img)
    return result

def make_face_img(img, mask, face_landmarks, face_img):
    mask, inverse_mask = prepare_mask(mask)
    img = img.astype(np.uint8)  # Apply color mapping for the eyes
    face_width = face_landmarks[0, 1]
    h, w, c = img.shape
    width_reduced = int((w-face_width)/8)
    face = img.copy()
    face = cv2.resize(face, (w*2, h*2))
    face = cv2.copyMakeBorder(face, 0, 0, int(width_reduced*0.3), int(width_reduced*0.3), cv2.BORDER_CONSTANT)
    face = cv2.resize(face, (w, h))
    face = cv2.GaussianBlur(face, (0, 0), 8)
    face = face.astype(float)/255
    result = multiply_eye_mask(mask, inverse_mask, face, img.astype(float)/255)
    return result

'''
def make_img(img, mask, face_landmarks, eyebrow_landmarks, face_img, type_mask):

    # Calculates inverse mask and reduces size of image. Then multiplies mask and image together.

    # Check if inputs are None
    if img is None:
        raise ValueError("Input image cannot be None.")
    if mask is None:
        raise ValueError("Mask cannot be None.")
    if face_landmarks is None:
        raise ValueError("Face landmarks cannot be None.")
    if eyebrow_landmarks is None:
        raise ValueError("Eyebrow landmarks cannot be None.")
    if face_img is None:
        raise ValueError("Face image cannot be None.")
    if type_mask is None:
        raise ValueError("Type mask cannot be None.")
    # Ensure mask and inverse_mask have the same number of channels as img
    if len(mask.shape) == 2:  # mask is grayscale
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Convert grayscale mask to BGR
    inverse_mask = cv2.bitwise_not(mask)  # Calculate inverse mask
    if len(inverse_mask.shape) == 2:  # inverse_mask is grayscale
        inverse_mask = cv2.cvtColor(inverse_mask, cv2.COLOR_GRAY2BGR)  # Convert grayscale inverse_mask to BGR
    # Convert masks to float to perform blending
    mask = mask.astype(float)/255
    inverse_mask = inverse_mask.astype(float)/255
    img = img.astype(np.uint8)  # Apply color mapping for the eyes
    # Find amount to reduce image
    face_width = face_landmarks[0, 1]
    eyebrow_height = eyebrow_landmarks[3, 1]
    h, w, c = img.shape
    height_reduced = int((h-eyebrow_height)/32)
    width_reduced = int((w-face_width)/8)
    # Convert eyes and face to 0-1 range
    face = img.copy()
    head = img.astype(float)/255
    if type_mask == 'mask':
        # Resize
        eye = cv2.copyMakeBorder(img, height_reduced, height_reduced*3, width_reduced, width_reduced, cv2.BORDER_CONSTANT)
        eye = cv2.resize(eye, (w, h))
        eye = eye.astype(float)/255
        # Multiply eyes and face by the mask
        result = multiply_eye_mask(mask, inverse_mask, eye, face_img)
    else:
        # Resize
        face = cv2.resize(face, (w*2, h*2))
        face = cv2.copyMakeBorder(face, 0, 0, int(width_reduced*0.3), int(width_reduced*0.3), cv2.BORDER_CONSTANT)
        face = cv2.resize(face, (w, h))
        face = cv2.GaussianBlur(face, (0, 0), 8)
        face = face.astype(float)/255
        # Multiply eyes and face by the mask
        result = multiply_eye_mask(mask, inverse_mask, face, head)
    return result
'''