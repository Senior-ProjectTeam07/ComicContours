# augment.py

import cv2
import numpy as np
import sys
import os

# Get the current and parent directory
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

# Import necessary modules
from augmentation.nose import resize_nose, create_nose_mask
<<<<<<< HEAD
<<<<<<< HEAD
from augmentation.mouth import resize_mouth, create_mouth_mask
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
from augmentation.eyes import create_eye_mask
from landmarking.load import load_feature_landmarks
from utils.file_utils import get_dir
from utils.img_utils import multi_res_blend, poisson_blend
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
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')
    # Create a mask for the nose
    nose_mask = create_nose_mask(original_img, nose_landmarks, width_margin_factor=0.4, height_margin_factor=0.1)
    # Blur the nose mask
    nose_mask_blurred = cv2.GaussianBlur(nose_mask, (0, 0), 21)
    # Blend the original image and the image with the resized nose
    img = img * (nose_mask_blurred / 255) + original_img * (1 - (nose_mask_blurred / 255))
    return img

<<<<<<< HEAD
<<<<<<< HEAD
# Function to augment the mouth of the image
def augment_mouth(img, img_path, facial_features, image_id, feature_to_int, mouth_scale_factor):
    # Read the image
    path_img = cv2.imread(img_path)
    # Make a copy of the original image
    original_img = path_img.copy()
    # Resize the mouth in the image
    img_mouth = resize_mouth(img, facial_features, image_id, feature_to_int, mouth_scale_factor)
    # Load the mouth landmarks
    mouth_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'lips')
    # Create a mask for the mouth
    mouth_mask = create_mouth_mask(original_img, mouth_landmarks, width_margin_factor=0.1, height_margin_factor=0.1)
    # Blur the mouth mask
    mouth_mask_blurred = cv2.GaussianBlur(mouth_mask, (0, 0), 21)
    # Blend the original image and the image with the resized mouth
    img = img_mouth * (mouth_mask_blurred / 255) + original_img * (1 - (mouth_mask_blurred / 255))
    return img

=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
# Function to augment the eyes of the image
def augment_eyes(img, facial_features, image_id, feature_to_int):
    # Load the eye, eyebrow, face, and nose landmarks
    eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
    eyebrow_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyebrows')
    face_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'jawline')
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')

    # Split eye_landmarks and eyebrow_landmarks into two
    modified_left_eye, modified_right_eye = np.array_split(eye_landmarks, 2)
    left_eyebrow, right_eyebrow = np.array_split(eyebrow_landmarks, 2)
    left_eye_original, right_eye_original = modified_left_eye.copy(), modified_right_eye.copy()

    # Delete outermost eyebrow landmark to make upper eye and eyebrow landmarks number the same
    left_eyebrow = np.delete(left_eyebrow, 3, 0)
    right_eyebrow = np.delete(right_eyebrow, 1, 0)

    # Delete bottom two eye landmarks
    modified_left_eye = np.delete(modified_left_eye, [4, 5], 0)
    modified_right_eye = np.delete(modified_right_eye, [4, 5], 0)

    # Expand eye_landmarks by half the distance from eyes to eyebrows
    left_eye_expansion = (modified_left_eye - left_eyebrow)
    right_eye_expansion = (modified_right_eye - right_eyebrow)

    # Make horizontal mask wider and expand eye near nose horizontal
    left_eye_expansion[0, 0] = -(face_landmarks[0, 0] - modified_left_eye[0, 0])/2
    right_eye_expansion[3, 0] = -((face_landmarks[16, 0] - modified_right_eye[3, 0])/2)
    left_eye_expansion[3, 0] = (modified_left_eye[3, 0] - nose_landmarks[0, 0])/2
    right_eye_expansion[0, 0] = -(nose_landmarks[0, 0] - modified_right_eye[0, 0])/2

    # Get the largest distance from results
    l_lower_expand = (left_eye_expansion[3, 1])
    r_lower_expand = (left_eye_expansion[3, 1])

    # Divide the expansions by 2
    left_eye_expansion, right_eye_expansion = left_eye_expansion / 2, right_eye_expansion / 2

    # Insert bottom eye landmarks and expand downward
    left_eye_expansion = np.append(left_eye_expansion, [[-(face_landmarks[0, 0] - modified_left_eye[0, 0])/2, -l_lower_expand/2]], axis=0)
    left_eye_expansion = np.insert(left_eye_expansion, 4, [-left_eye_expansion[0, 0], -l_lower_expand], axis=0)
    right_eye_expansion = np.append(right_eye_expansion, [[right_eye_expansion[3, 0], -r_lower_expand]], axis=0)
    right_eye_expansion = np.insert(right_eye_expansion, 4, [-(face_landmarks[16, 0] - modified_right_eye[3, 0])/2, -r_lower_expand/2], axis=0)

    # Calculate expanded result into eye_landmarks
    eye_landmarks1, eye_landmarks2 = left_eye_original - left_eye_expansion,  right_eye_original - right_eye_expansion

    # Create mask for eyes
    reduced_eyes_mask = create_eye_mask(eye_landmarks1, eye_landmarks2, img)

    # Create mask2 for eyes
    eye_landmarks1[0, 0] = eye_landmarks1[0, 0]+((face_landmarks[0, 0] - eye_landmarks1[0, 0])/2)  # make horizontal mask wider
    eye_landmarks2[3, 0] = eye_landmarks2[3, 0]+((face_landmarks[16, 0] - eye_landmarks2[3, 0])/2)  # make horizontal mask wider

    # Check if the 6th element exists before trying to access it
    if eye_landmarks1.shape[0] > 5:
        eye_landmarks1[5, 0] = eye_landmarks1[5, 0]-(face_landmarks[16, 0] - eye_landmarks2[3, 0])  # make horizontal mask wider

    if eye_landmarks2.shape[0] > 4:
        eye_landmarks2[4, 0] = eye_landmarks2[4, 0]+(face_landmarks[16, 0] - eye_landmarks2[3, 0])  # make horizontal mask wider

    blurred_eyes_mask = create_eye_mask(eye_landmarks1, eye_landmarks2, img)

    # Blur the mask to obtain natural result
    blur = (3*int(left_eye_expansion[0, 0]))
    if not(blur % 2):
        blur = blur + 1
    reduced_eyes_mask = cv2.GaussianBlur(reduced_eyes_mask, (blur, blur), 99)
    blurred_eyes_mask = cv2.GaussianBlur(blurred_eyes_mask, (99, 99), 32)

    # Put masks into image
    result = make_img(img, blurred_eyes_mask, face_landmarks, eyebrow_landmarks, img, "blurred_eyes_mask")
    result = make_img(img, reduced_eyes_mask, face_landmarks, eyebrow_landmarks, result, "reduced_eyes_mask")
    result = cv2.normalize(result, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    return result

# Function to augment the image
def augment_image():
    # Load facial features from numpy file
    facial_features = np.load(get_dir('data/facial_features.npy'))
    # Map facial features to integers
    feature_to_int = {'jawline': 0, 'eyebrows': 1, 'nose': 2, 'eyes': 3, 'lips': 4}
    # Define directories for original and augmented images
    image_directory = get_dir('data/original_images')
    augmented_directory = get_dir('data/augmented_images')
    # Define scale factor for nose augmentation
    nose_scale_factor = 1.25
<<<<<<< HEAD
<<<<<<< HEAD
    mouth_scale_factor = 1.25
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96

    # Create directory for augmented images if it doesn't exist
    if not os.path.exists(augmented_directory):
        os.makedirs(augmented_directory)

    # Get list of image paths from the image directory
    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Loop through each image path
    for img_path in image_paths:
        # Get the index of the current image path
        image_id = image_paths.index(img_path)
        # Augment the nose of the image
        img = augment_nose(img_path, facial_features, image_id, feature_to_int, nose_scale_factor)
<<<<<<< HEAD
<<<<<<< HEAD
        img = augment_mouth(img, img_path, facial_features, image_id, feature_to_int, mouth_scale_factor)
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
        # Augment the eyes of the image
        img = augment_eyes(img, facial_features, image_id, feature_to_int)
        # Define the name and path for the augmented image
        augmented_img_name = f"augmented_{os.path.basename(img_path)}"
        augmented_img_path = os.path.join(augmented_directory, augmented_img_name)
        # Save the augmented image
<<<<<<< HEAD
<<<<<<< HEAD
        cv2.imwrite(augmented_img_path, img)
=======
        cv2.imwrite(augmented_img_path, img)
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
        cv2.imwrite(augmented_img_path, img)
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
