# test_eyes.py

import unittest
from unittest.mock import patch
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.eyes import resize_eyes, create_eye_mask

class TestEyes(unittest.TestCase):
    def setUp(self):
        self.img = np.zeros((500, 500, 3), dtype=np.uint8)
        self.image_id = 0
        self.feature_to_int = {'Eyes': 1}
        self.scale_factor = 1.25
        self.invalid_scale_factor = 3.1
        self.facial_features = np.array([[self.image_id, self.feature_to_int['Eyes'], 0, 100, 100],
                                         [self.image_id, self.feature_to_int['eyes'], 0, 400, 400]])

    @patch('augmentation.eyes.load_feature_landmarks')
    @patch('augmentation.eyes.resize_and_overlay_feature')
    def test_resize_eyes(self, mock_resize_and_overlay, mock_load_feature_landmarks):
        mock_load_feature_landmarks.return_value = self.facial_features[:, 3:5]
        resize_eyes(self.img, self.facial_features, self.image_id, self.feature_to_int, self.scale_factor)
        mock_load_feature_landmarks.assert_called_with(self.facial_features, self.image_id, self.feature_to_int, 'eyes')

    @patch('augmentation.eyes.load_feature_landmarks')
    @patch('augmentation.eyes.resize_and_overlay_feature')
    def test_invalid_scale_factor(self, mock_resize_and_overlay, mock_load_feature_landmarks):
        with self.assertRaises(ValueError):
            resize_eyes(self.img, self.facial_features, self.image_id, self.feature_to_int, self.invalid_scale_factor)
        
    def test_no_data_for_image_id(self):
        with self.assertRaises(ValueError):
            resize_eyes(self.img, self.facial_features[self.facial_features[:, 0] != self.image_id], self.image_id, self.feature_to_int, self.scale_factor)

    def test_no_data_for_eyes_feature(self):
        with self.assertRaises(ValueError):
            resize_eyes(self.img, self.facial_features[self.facial_features[:, 1] != self.feature_to_int['eyes']], self.image_id, self.feature_to_int, self.scale_factor)

    def test_non_3d_image(self):
        grayscale_img = np.zeros((500, 500), dtype=np.uint8)
        with self.assertRaises(ValueError):
            resize_eyes(grayscale_img, self.facial_features, self.image_id, self.feature_to_int, self.scale_factor)
    
    def test_create_eye_mask(self):
        feature_points = np.array([[100, 100], [400, 400]])
        mask = create_eye_mask(feature_points, feature_points, self.img)
        self.assertEqual(mask.shape, self.img.shape)
        self.assertTrue((mask[100:400, 100:400] == 255).all())

    def test_negative_zero_scale_factor(self):
        with self.assertRaises(ValueError):
            resize_eyes(self.img, self.facial_features, self.image_id, self.feature_to_int, -1)
            resize_eyes(self.img, self.facial_features, self.image_id, self.feature_to_int, 0)

    def test_scale_factor_greater_than_three(self):
        with self.assertRaises(ValueError):
            resize_eyes(self.img, self.facial_features, self.image_id, self.feature_to_int, 3.1)

    def test_non_numeric_scale_factor(self):
        with self.assertRaises(ValueError):
            resize_eyes(self.img, self.facial_features, self.image_id, self.feature_to_int, 'invalid')

    def test_feature_points_with_incorrect_columns(self):
        feature_points = np.array([[100, 100], [400, 400]])
        with self.assertRaises(ValueError):
            create_eye_mask(feature_points, feature_points, self.img)
        feature_points = np.array([[100], [400]])
        with self.assertRaises(ValueError):
            create_eye_mask(feature_points, feature_points, self.img)

if __name__ == '__main__':
    unittest.main()