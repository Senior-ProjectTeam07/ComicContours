# test_augment.py

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.augment import main

class TestAugmentingFeatures(unittest.TestCase):
    
    def setUp(self):
        # Set up a dummy image with the correct shape
        self.dummy_image = np.zeros((4032, 3024, 3), dtype=np.uint8)
        self.dummy_features = np.array([[10, 10], [20, 20]])
        self.dummy_image_id = 0

    @patch('augmentation.augment.cv2.imread')
    @patch('os.listdir')
    @patch('utils.file_utils.get_dir')
    @patch('augmentation.nose.resize_nose')
    @patch('landmarking.load.load_feature_landmarks')
    @patch('augmentation.nose.create_nose_mask')
    @patch('cv2.GaussianBlur')
    def test_main(self, mock_blur, mock_create_mask, mock_load_landmarks, mock_resize_nose, mock_get_dir, mock_listdir, mock_imread):
        # Mock the dependencies that interact with the file system
        mock_get_dir.side_effect = lambda x: '/test/dir/' + x
        mock_listdir.return_value = ['image1.jpg', 'image2.png']
        mock_imread.return_value = self.dummy_image

        # Mock the image processing functions
        mock_load_landmarks.return_value = self.dummy_features
        mock_create_mask.return_value = self.dummy_image
        mock_blur.return_value = self.dummy_image
        mock_resize_nose.return_value = self.dummy_image

        # Run the function under test
        main()

        # Verify that the image processing functions were called correctly
        # Verify other mocks/assertions as needed
        mock_resize_nose.assert_called()
        mock_create_mask.assert_called()
        mock_blur.assert_called()

if __name__ == '__main__':
    unittest.main()
