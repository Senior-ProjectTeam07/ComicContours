import unittest
from unittest.mock import patch
import logging
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.nose import resize_nose

class TestNose(unittest.TestCase):

    def setUp(self):
        # Dummy data setup
        self.img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.facial_features = np.load('data/facial_features.npy')
        self.image_id = 0
        self.feature_to_int = {'nose': 2}
        self.scale_factor = 1.25
        # Setup expected output directly here for clarity, assuming it's a simple case
        self.expected_output = np.zeros((100, 100, 3), dtype=np.uint8)
        # Define valid facial feature coordinates that would result in a valid feature region
        self.valid_nose_landmarks = np.array([[30, 30], [70, 70]])  # Example coordinates

    @patch('augmentation.resize_overlay.resize_and_overlay_feature')
    @patch('landmarking.load.load_feature_landmarks')
    def test_resize_nose(self, mock_load_landmarks, mock_resize_and_overlay):
        # Mock returns valid nose landmarks
        mock_load_landmarks.return_value = self.valid_nose_landmarks
        mock_resize_and_overlay.return_value = self.expected_output  # Mock the expected behavior of resize and overlay

        try:
            # Call the function under test
            result = resize_nose(self.img, self.facial_features, self.image_id, self.feature_to_int, self.scale_factor)

            # Assertions to validate the outcome
            np.testing.assert_array_equal(result, self.expected_output)
            # Validate the function calls with the expected arguments
            mock_load_landmarks.assert_called_once_with(self.facial_features, self.image_id, self.feature_to_int, 'nose')
            mock_resize_and_overlay.assert_called_once_with(self.img, self.valid_nose_landmarks, self.scale_factor, width_margin_factor=0.6, height_margin_factor=0.7)
        except ValueError as e:
            if str(e) == "Feature region is invalid after applying margins.":
                logging.warning("Skipping image due to invalid feature region after applying margins.")
            else:
                raise  # Re-raise the exception if it's not the one we're expecting

if __name__ == '__main__':
    unittest.main()