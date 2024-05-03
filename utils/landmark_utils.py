# landmark_utils.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import numpy as np
from collections import OrderedDict

# Define an ordered dictionary for the 68 facial landmarks for easy reference
FACIAL_LANDMARKS_68_IDX = OrderedDict([
    ("Outer_Lip", (48, 60)),  # Indices for the outer contour of the lips
    ("Inner_Lip", (60, 68)),  # Indices for the inner contour of the lips
    ("Right_Eyebrow", (17, 22)),
    ("Left_Eyebrow", (22, 27)),
    ("Right_Eye", (36, 42)),
    ("Left_Eye", (42, 48)),
    ("Nose", (27, 36)),       # Adjusted to correctly define the end index
    ("Jaw", (0, 17))
])

# Map the keys in FACIAL_LANDMARKS_68_IDX to integers
feature_to_int = {feature: i for i, feature in enumerate(FACIAL_LANDMARKS_68_IDX.keys())}

# Reverse mapping from integers to feature names
int_to_feature = {i: feature for feature, i in feature_to_int.items()}
assert 'Outer_Lip' in int_to_feature.values()

# This allows us to access the indexes dynamically, for example:
# FACIAL_LANDMARKS_68_IDX["Mouth"] would return (48, 68),
# which are the start and end indexes for the mouth in the 68-point model.

# Mapping keys to FACIAL_LANDMARKS_68_IDX keys
key_mapping = {
    'jawline': 'Jaw',
    'eyebrows': ['Right_Eyebrow', 'Left_Eyebrow'],
    'nose': 'Nose',
    'eyes': ['Right_Eye', 'Left_Eye'],
    'lips': ['Outer_Lip', 'Inner_Lip'],  # Updated to reflect the split into outer and inner lips
}