# load.py

import sys
import os

# Ensure the current and parent directories are in the path for module imports
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX

def load_feature_landmarks(facial_features, image_id, feature_to_int, feature_name):
    """
    Load facial feature landmarks for a given image ID and feature name.
    """
    if facial_features.size == 0 or len(facial_features.shape) != 2:
        raise ValueError("facial_features array is empty or not correctly formatted.")
    # Ensure facial_features has at least 3 columns
    #if facial_features.shape[1] < 3:
        #raise ValueError("facial_features must have at least 3 columns.")
    # Validate feature_name against FACIAL_LANDMARKS_68_IDX
    if feature_name not in FACIAL_LANDMARKS_68_IDX:
        raise ValueError(f"'{feature_name}' is not a valid feature. Please use one of {list(FACIAL_LANDMARKS_68_IDX.keys())}.")
    
    feature_start, feature_end = FACIAL_LANDMARKS_68_IDX[feature_name]
    mask = (facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_to_int.get(feature_name, -1)) & (facial_features[:, 2] >= feature_start) & (facial_features[:, 2] < feature_end)
    filtered_landmarks = facial_features[mask]
    
    if filtered_landmarks.size == 0:
        raise ValueError(f"No landmarks found for image_id {image_id} and feature '{feature_name}'.")
    
    return filtered_landmarks[:, 3:5]