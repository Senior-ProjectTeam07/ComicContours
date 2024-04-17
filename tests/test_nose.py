import unittest
from unittest.mock import patch
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.nose import resize_nose, create_nose_mask

class TestNose(unittest.TestCase):
    def setUp(self):
        self.img = np.zeros((500, 500, 3), dtype=np.uint8)
        self.image_id = 0
        self.feature_to_int = {'Nose': 2}
        self.scale_factor = 1.25
        self.invalid_scale_factor = 3.1
        self.facial_features = np.array([[self.image_id, self.feature_to_int['Nose'], 0, 100, 100],
                                         [self.image_id, self.feature_to_int['Nose'], 0, 400, 400]])

    @patch('augmentation.nose.load_feature_landmarks')
    @patch('augmentation.nose.resize_and_overlay_feature')
    def test_resize_nose(self, mock_resize_and_overlay, mock_load_feature_landmarks):
        mock_load_feature_landmarks.return_value = self.facial_features[:, 3:5]
        resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, self.scale_factor)

        # Get the arguments that load_feature_landmarks was last called with
        load_args, _ = mock_load_feature_landmarks.call_args

        # Verify that the correct indices were used to access the nose features
        self.assertEqual(type(load_args[2]), dict)
        self.assertEqual(load_args[2]['Nose'], self.feature_to_int['Nose'])
        self.assertEqual(load_args[3], 'Nose')

        mock_load_feature_landmarks.assert_called_with(self.facial_features, self.image_id, self.feature_to_int, 'Nose')

    @patch('augmentation.nose.load_feature_landmarks')
    @patch('augmentation.nose.resize_and_overlay_feature')
    def test_invalid_scale_factor(self, mock_resize_and_overlay, mock_load_feature_landmarks):
        with self.assertRaises(ValueError):
            resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, self.invalid_scale_factor)
        
    def test_no_data_for_image_id(self):
        with self.assertRaises(ValueError):
            resize_nose(self.img, self.facial_features[self.facial_features[:, 0] != self.image_id], self.image_id, self.feature_to_int, self.scale_factor)

    def test_no_data_for_nose_feature(self):
        with self.assertRaises(ValueError):
            resize_nose(self.img, self.facial_features[self.facial_features[:, 1] != self.feature_to_int['Nose']], self.image_id, self.feature_to_int, self.scale_factor)

    def test_non_3d_image(self):
        grayscale_img = np.zeros((500, 500), dtype=np.uint8)
        with self.assertRaises(ValueError):
            resize_nose(grayscale_img, self.facial_features, self.image_id, self.feature_to_int, self.scale_factor)
    
    def test_create_nose_mask(self):
        feature_points = np.array([[100, 100], [400, 400]])
        width_margin_factor = 0.6
        height_margin_factor = 0.7
        mask = create_nose_mask(self.img, feature_points, width_margin_factor, height_margin_factor)
        self.assertEqual(mask.shape, self.img.shape)
        self.assertTrue((mask[100:400, 100:400] == 255).all())

    def test_negative_zero_scale_factor(self):
        with self.assertRaises(ValueError):
            resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, -1)
            resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, 0)

    def test_scale_factor_greater_than_three(self):
        with self.assertRaises(ValueError):
            resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, 3.1)

    def test_non_numeric_scale_factor(self):
        with self.assertRaises(ValueError):
            resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, 'invalid')

    def test_feature_points_with_incorrect_columns(self):
        feature_points = np.array([[100, 100, 100], [400, 400, 400]])
        with self.assertRaises(ValueError):
            create_nose_mask(self.img, feature_points, 0.6, 0.7)
        feature_points = np.array([[100], [400]])
        with self.assertRaises(ValueError):
            create_nose_mask(self.img, feature_points, 0.6, 0.7)

    def test_margin_factor_out_of_range(self):
        feature_points = np.array([[100, 100], [400, 400]])
        with self.assertRaises(ValueError):
            create_nose_mask(self.img, feature_points, -0.1, 0.7)
            create_nose_mask(self.img, feature_points, 1.1, 0.7)
            create_nose_mask(self.img, feature_points, 0.6, -0.1)
            create_nose_mask(self.img, feature_points, 0.6, 1.1)

    def test_non_numeric_margin_factor(self):
        feature_points = np.array([[100, 100], [400, 400]])
        with self.assertRaises(ValueError):
            create_nose_mask(self.img, feature_points, 'invalid', 0.7)
            create_nose_mask(self.img, feature_points, 0.6, 'invalid')

if __name__ == '__main__':
    unittest.main()