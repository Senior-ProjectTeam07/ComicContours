# Author: Rhiannon Barber
# This file is a 'dummy' file for how the scale factors can be integrated into the augm.
# system. Does NOT actually augment.

import cv2
import numpy as np
import os
from pathlib import Path

def get_dir(filename):
    base_dir = Path(__file__).resolve().parent
    return base_dir.joinpath(filename).resolve()

def load_scale_factors(npy_path):
    scale_factors = np.load(npy_path, allow_pickle=True).item()
    return scale_factors

def load_feature_landmarks(facial_features, image_id, feature_to_int, feature_name):
    feature_landmarks = facial_features[
        (facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_to_int[feature_name])]
    return feature_landmarks[:, 3:5]

# just an example of how to use it, where if greater than 1 increase by 10% per tenth greater
# same for less than one, decrease by 10%. I figured we can mess with the percentages if 10% at a time wasn't
# augmenting enough.
# This uses a conditional operator currently, we can expand it if needed.

def calculate_scale_factor(base_scale, scale_deviation):
    return base_scale + (scale_deviation - 1) * 0.1 if scale_deviation > 1 else base_scale - (1 - scale_deviation) * 0.1

def main():
    # example of the file loading, just again for demo purposes.

    images_directory = get_dir('user_photos')
    augmented_directory = get_dir('augmented_user_photos')
    os.makedirs(augmented_directory, exist_ok=True)
    landmarks_filepath = get_dir('user_photos_features.csv')
    deviations_filepath = get_dir('user_features.csv')
    images = load_images(images_directory)
    landmarks = load_landmarks(landmarks_filepath)
    scale_deviations = load_feature_data(deviations_filepath)
    for img_id, image in images.items():
        left_eye_landmarks = extract_eye_landmarks(landmarks, int(img_id), 3)
        right_eye_landmarks = extract_eye_landmarks(landmarks, int(img_id), 4)
        left_scale_factor = calculate_scale_factor(1.0, scale_deviations[3])  # does the calc based on the
        right_scale_factor = calculate_scale_factor(1.0, scale_deviations[4])  # scale dev from file.

        # can expand to all features, just did eyes for demonstration purposes.
        # augmenting after


