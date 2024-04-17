# augment.py

import cv2
import numpy as np
import sys
import os

# Get the current and parent directory
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.landmark_utils import feature_to_int

# Import necessary modules
from augmentation.nose import resize_nose, create_nose_mask
from augmentation.eyes import create_eye_mask, resize_eyes
from landmarking.load import load_feature_landmarks
from utils.file_utils import get_dir
from utils.img_utils import multi_res_blend, poisson_blend
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX
from augmentation.make_image import make_img

# Function to augment the nose of the image
def augment_nose(img_path, facial_features, image_id, feature_to_int, nose_scale_factor):
    # Read the image
    img = cv2.imread(img_path)
    # Make a copy of the original image
    original_img = img.copy()
    # Resize the nose in the image
    img = resize_nose(img, facial_features, image_id, feature_to_int, nose_scale_factor)
    # Load the nose landmarks
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'Nose')
    # Create a mask for the nose
    nose_mask = create_nose_mask(original_img, nose_landmarks, width_margin_factor=0.4, height_margin_factor=0.1)
    # Blur the nose mask
    nose_mask_blurred = cv2.GaussianBlur(nose_mask, (0, 0), 21)
    # Blend the original image and the image with the resized nose
    img = img * (nose_mask_blurred / 255) + original_img * (1 - (nose_mask_blurred / 255))
    return img

# Function to augment the eyes of the image
def augment_eyes(img_path, facial_features, image_id, feature_to_int, eyes_scale_factor):
    # Read the image
    img = cv2.imread(img_path)
    # Make a copy of the original image
    original_img = img.copy()

    # Load the eye landmarks
    right_eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'Right_Eye')
    left_eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'Left_Eye')

    # Resize and augment each eye separately
    img = resize_eyes(img, facial_features, image_id, feature_to_int, eyes_scale_factor)

    # Create a mask for each eye and blend the original image and the image with the resized eyes
    for eye_landmarks in [right_eye_landmarks, left_eye_landmarks]:
        eye_mask = create_eye_mask(eye_landmarks, original_img)
        eye_mask_blurred = cv2.GaussianBlur(eye_mask, (0, 0), 21)
        img = img * (eye_mask_blurred / 255) + original_img * (1 - (eye_mask_blurred / 255))

    return img

# Function to augment the image
def augment_image():
    # Load facial features from numpy file
    facial_features = np.load(get_dir('data/facial_features.npy'))
    # Define directories for original and augmented images
    image_directory = get_dir('data/original_images')
    augmented_directory = get_dir('data/augmented_images')
    # Define scale factor for nose augmentation
    nose_scale_factor = 1.25
    eyes_scale_factor = 1.25
    
    # Get list of image paths from the image directory
    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Loop through each image path
    for img_path in image_paths:
        # Get the index of the current image path
        image_id = image_paths.index(img_path)
        # Augment the nose of the image
        img = augment_nose(img_path, facial_features, image_id, feature_to_int, nose_scale_factor)
        # Augment the eyes of the image
        img = augment_eyes(img_path, facial_features, image_id, feature_to_int, eyes_scale_factor)
        # Define the name and path for the augmented image
        augmented_img_name = f"augmented_{os.path.basename(img_path)}"
        augmented_img_path = os.path.join(augmented_directory, augmented_img_name)
        # Save the augmented image
        cv2.imwrite(augmented_img_path, img)