import unittest
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.resize_overlay import resize_and_overlay_feature

class TestResizeAndOverlayFeature(unittest.TestCase):

    def setUp(self):
        # Dummy data setup
        self.img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.feature_points = np.array([[30, 30], [70, 70]])
        self.scale_factor = 1.25
        self.width_margin_factor = 0.3
        self.height_margin_factor = 0.4

    def test_resize_and_overlay_feature(self):
        # Call the function under test
        result = resize_and_overlay_feature(self.img, self.feature_points, self.scale_factor, self.width_margin_factor, self.height_margin_factor)

        # Assertions to validate the outcome
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.img.shape)

    def test_resize_and_overlay_feature_with_invalid_image(self):
        # Test with an empty image
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(np.array([]), self.feature_points, self.scale_factor, self.width_margin_factor, self.height_margin_factor)

    def test_resize_and_overlay_feature_with_invalid_feature_points(self):
        # Test with empty feature points
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, np.array([]), self.scale_factor, self.width_margin_factor, self.height_margin_factor)

        # Test with feature points that result in an invalid region
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, np.array([[30, 30], [30, 30]]), self.scale_factor, self.width_margin_factor, self.height_margin_factor)
    
    def test_resize_and_overlay_feature_with_invalid_scale_factor(self):
        # Test with a scale factor less than or equal to 0
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, self.feature_points, 0, self.width_margin_factor, self.height_margin_factor)

        # Test with a scale factor greater than 1
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, self.feature_points, 5.1, self.width_margin_factor, self.height_margin_factor)

    def test_resize_and_overlay_feature_with_invalid_margin_factors(self):
        # Test with width and height margin factors less than 0
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, self.feature_points, self.scale_factor, -0.1, -0.1)

        # Test with width and height margin factors greater than 1
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, self.feature_points, self.scale_factor, 1.1, 1.1)

    def test_resize_and_overlay_feature_with_feature_points_outside_image(self):
        # Test with feature points outside the bounds of the image
        with self.assertRaises(ValueError):
            resize_and_overlay_feature(self.img, np.array([[200, 200], [300, 300]]), self.scale_factor, self.width_margin_factor, self.height_margin_factor)

if __name__ == '__main__':
    unittest.main()