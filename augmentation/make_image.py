# make_image.py

import cv2
import numpy as np
import sys
import os

# Get the current directory and parent directory for importing modules
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

# Import necessary modules
from augmentation.eyes import multiply_eye_mask
from utils.img_utils import poisson_blend

def check_inputs(img, mask, face_landmarks, eyebrow_landmarks, face_img, type_mask):
    # Function to check if any of the inputs are None, if so, raise a ValueError
    # This is to ensure that all necessary inputs are provided for the image processing

    # List of inputs to check
    inputs = [img, mask, face_landmarks, eyebrow_landmarks, face_img, type_mask]
    # Corresponding names for the inputs to provide meaningful error messages
    input_names = ["Input image", "Mask", "Face landmarks", "Eyebrow landmarks", "Face image", "Type mask"]

    for i, input in enumerate(inputs):
        if input is None:
            raise ValueError(f"{input_names[i]} cannot be None.")

def prepare_masks(mask):
    # Function to prepare the mask and its inverse for image processing
    # The mask is used to isolate the area of interest in the image
    # The inverse mask is used to isolate the rest of the image

    # If the mask is grayscale, convert it to BGR for compatibility with the image
    if len(mask.shape) == 2:
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    # Calculate the inverse mask
    inverse_mask = cv2.bitwise_not(mask)
    # If the inverse mask is grayscale, convert it to BGR for compatibility with the image
    if len(inverse_mask.shape) == 2:
        inverse_mask = cv2.cvtColor(inverse_mask, cv2.COLOR_GRAY2BGR)
    # Convert the masks to float for blending operations
    mask = mask.astype(float)/255
    inverse_mask = inverse_mask.astype(float)/255
    return mask, inverse_mask

def calculate_reductions(face_landmarks, eyebrow_landmarks, img):
    # Function to calculate the amount to reduce the image size by
    # This is based on the face and eyebrow landmarks to ensure the face is properly centered in the image

    # Get the width of the face and the height of the eyebrows from the landmarks
    face_width = face_landmarks[0, 1]
    eyebrow_height = eyebrow_landmarks[3, 1]
    # Get the dimensions of the image
    h, w, c = img.shape
    # Calculate the amount to reduce the height and width by
    height_reduced = int((h-eyebrow_height)/32)
    width_reduced = int((w-face_width)/8)
    return height_reduced, width_reduced, h, w, c

def make_eye_img(img, height_reduced, width_reduced, w, h, mask, inverse_mask, face_img):
    # Function to create the eye image
    # The image is resized and the mask is applied to isolate the eyes

    # Add a border to the image and resize it
    eye = cv2.copyMakeBorder(img, height_reduced, height_reduced*3, width_reduced, width_reduced, cv2.BORDER_CONSTANT)
    eye = cv2.resize(eye, (w, h))
    # Convert the image to float for blending operations
    eye = eye.astype(float)/255
    # Apply the mask to the image to isolate the eyes
    return multiply_eye_mask(mask, inverse_mask, eye, face_img)

def make_face_img(img, width_reduced, w, h, mask, inverse_mask):
    # Function to create the face image
    # The image is resized, blurred, and the mask is applied to isolate the face

    # Copy the image and convert it to float for blending operations
    face = img.copy()
    head = img.astype(float)/255
    # Resize the image and add a border
    face = cv2.resize(face, (w*2, h*2))
    face = cv2.copyMakeBorder(face, 0, 0, int(width_reduced*0.3), int(width_reduced*0.3), cv2.BORDER_CONSTANT)
    face = cv2.resize(face, (w, h))
    # Apply a Gaussian blur to the image
    face = cv2.GaussianBlur(face, (0, 0), 8)
    # Convert the image to float for blending operations
    face = face.astype(float)/255
    # Apply the mask to the image to isolate the face
    return  multiply_eye_mask(mask, inverse_mask, face, head)

def make_img(img, mask, face_landmarks, eyebrow_landmarks, face_img, type_mask):
    # Main function to create the final image
    # The function checks the inputs, prepares the masks, calculates the reductions, and creates the eye or face image based on the type mask

    # Check the inputs
    check_inputs(img, mask, face_landmarks, eyebrow_landmarks, face_img, type_mask)
    # Prepare the masks
    mask, inverse_mask = prepare_masks(mask)
    # Convert the image to uint8 for color mapping
    img = img.astype(np.uint8)
    # Calculate the reductions
    height_reduced, width_reduced, h, w, c = calculate_reductions(face_landmarks, eyebrow_landmarks, img)
    # Create the eye or face image based on the type mask
    if type_mask == 'reduced_eyes_mask':
        result = make_eye_img(img, height_reduced, width_reduced, w, h, mask, inverse_mask, face_img)
    else:
        result = make_face_img(img, width_reduced, w, h, mask, inverse_mask)
    return result