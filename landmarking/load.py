# load.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import numpy as np
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int

def load_feature_landmarks(facial_features, image_id, feature_name):
    '''
    This function loads the landmarks for a specific facial feature from the facial features data.
    The facial features data is a numpy array where each row represents a landmark point.
    The columns represent the image ID, feature ID, landmark index, and x and y coordinates respectively.
    The function returns a 2D numpy array where each row represents a landmark point and the columns represent the x and y coordinates.
    '''
    # Validate input parameters
    if not isinstance(facial_features, np.ndarray) or facial_features.shape[1] != 5:
        raise ValueError("Facial features data must be a numpy array with 5 columns.")
    if not isinstance(image_id, int):
        raise ValueError("Image ID must be an integer.")
    if not isinstance(feature_name, str):
        raise ValueError("Feature name must be a string.")
    if facial_features.size == 0:
        raise ValueError("Facial features data must not be empty.")
    
    # Get the feature ID for the given feature name
    feature_id = feature_to_int.get(feature_name)
    if feature_id is None:
        raise ValueError(f"Invalid feature name: {feature_name}")
    
    # Extract the landmarks for the given image ID and feature ID
    landmarks = facial_features[(facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_id)]
    
    # Check if any landmarks were found
    if landmarks.size == 0:
        return np.array([])
    
    # Return the x and y coordinates of the landmarks
    return landmarks[:, 3:5]