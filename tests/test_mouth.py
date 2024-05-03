# test_mouth.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import unittest
import numpy as np
# test_mouth.py
from unittest.mock import patch
from augmentation.mouth import resize_mouth, create_mouth_mask, multiply_mouth_mask

class TestMouth(unittest.TestCase):
    def setUp(self):
        self.img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.facial_features = np.array([
            [30, 40],  # Outer_Lip
            [70, 40],  # Inner_Lip
            [50, 60],
            [30, 80],
            [70, 80]
        ])
        self.image_id = 0
        self.feature_to_int = {'Outer_Lip': 0, 'Inner_Lip': 1}
        self.scale_factor = 1.5

    @patch('augmentation.mouth.load_feature_landmarks')
    def test_resize_mouth(self, mock_load_feature_landmarks):
        mock_load_feature_landmarks.return_value = np.array([
            [30, 40],  # Outer_Lip
            [70, 40],  # Inner_Lip
            [50, 60],
            [30, 80],
            [70, 80]
        ])
        try:
            resized_img = resize_mouth(self.img, self.facial_features, self.image_id, self.feature_to_int, self.scale_factor)
            self.assertEqual(resized_img.shape, self.img.shape)
        except Exception as e:
            self.fail(f"resize_mouth raised Exception unexpectedly: {e}")

    def test_create_mouth_mask(self):
        try:
            mask = create_mouth_mask(self.img, self.facial_features, 0.1, 0.1)
            self.assertEqual(mask.shape, self.img.shape)
        except Exception as e:
            self.fail(f"create_mouth_mask raised Exception unexpectedly: {e}")

    def test_multiply_mouth_mask(self):
        # Create two mouth masks
        mouth_mask1 = np.zeros((100, 100), dtype=np.uint8)
        mouth_mask2 = np.zeros((100, 100), dtype=np.uint8)
        mouth_mask1[40:60, 40:60] = 255
        mouth_mask2[60:80, 60:80] = 255

        # Create an original image
        original_img = np.copy(self.img)
        original_img[40:60, 40:60, :] = 255
        original_img[60:80, 60:80, :] = 255

        try:
            result = multiply_mouth_mask(mouth_mask1, mouth_mask2, self.img, original_img)
            self.assertEqual(result.shape, self.img.shape)
        except Exception as e:
            self.fail(f"multiply_mouth_mask raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()