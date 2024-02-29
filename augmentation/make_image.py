# make_image.py

import cv2
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.eyes import multiply_eye_mask

# Calculates inverse mask and reduces size of image. Then multiplies mask and image together.
def make_img(img, mask, face_landmarks, eyebrow_landmarks, face_img, type_mask):
    inverse_mask = cv2.bitwise_not(mask)  # Calculate inverse mask
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