# landmark_utils.py

import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from collections import OrderedDict

# Define an ordered dictionary for the 68 facial landmarks for easy reference
FACIAL_LANDMARKS_68_IDX = OrderedDict([
    ("Mouth", (48, 68)),
    ("Right_Eyebrow", (17, 22)),
    ("Left_Eyebrow", (22, 27)),
    ("Right_Eye", (36, 42)),
    ("Left_Eye", (42, 48)),
    ("Nose", (27, 35)),
    ("Jaw", (0, 17))
])

# Map the keys in FACIAL_LANDMARKS_68_IDX to integers
feature_to_int = {feature: i for i, feature in enumerate(FACIAL_LANDMARKS_68_IDX.keys())}

# This allows us to access the indexes dynamically, for example:
# FACIAL_LANDMARKS_68_IDX["Mouth"] would return (48, 68),
# which are the start and end indexes for the mouth in the 68-point model.
