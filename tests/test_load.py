# test_load.py

import unittest
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int
from landmarking.load import load_feature_landmarks

class TestLoad(unittest.TestCase):
    def setUp(self):
        self.facial_features = np.load(get_dir('data/facial_features.npy'))
        self.image_id = 0
        self.feature_to_int = feature_to_int

    def test_load_feature_landmarks(self):
        for feature_name in FACIAL_LANDMARKS_68_IDX.keys():
            landmarks = load_feature_landmarks(self.facial_features, self.image_id, self.feature_to_int, feature_name)
            self.assertIsNotNone(landmarks)
            self.assertTrue(landmarks.shape[1] == 2)  # x and y coordinates

    def test_invalid_feature_name(self):
        with self.assertRaises(ValueError):
            load_feature_landmarks(self.facial_features, self.image_id, self.feature_to_int, 'invalid_feature')

    def test_empty_facial_features(self):
        with self.assertRaises(ValueError):
            load_feature_landmarks(np.array([]), self.image_id, self.feature_to_int, list(FACIAL_LANDMARKS_68_IDX.keys())[0])

    def test_no_landmarks_found(self):
        with self.assertRaises(ValueError):
            load_feature_landmarks(self.facial_features, max(self.facial_features[:, 0]) + 1, self.feature_to_int, list(FACIAL_LANDMARKS_68_IDX.keys())[0])

if __name__ == '__main__':
    unittest.main()