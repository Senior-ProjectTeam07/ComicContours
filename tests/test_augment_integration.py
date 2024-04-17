# test_augment_integration.py

import unittest
from unittest import mock 
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.augment import augment_image, augment_nose, augment_eyes

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
    @patch('augmentation.augment.augment_nose')
    @patch('augmentation.augment.augment_eyes')
    @patch('cv2.GaussianBlur')
    @patch('cv2.imwrite')
    def test_augment_image(self, mock_imwrite, mock_blur, mock_augment_nose, 
                       mock_augment_eyes, mock_create_mask, mock_load_landmarks, 
                       mock_resize_nose, mock_get_dir, mock_listdir, mock_imread):
        # Mock the dependencies that interact with the file system
        mock_get_dir.side_effect = lambda x: '/test/dir/' + x
        mock_listdir.return_value = ['image1.jpg', 'image2.png']
        mock_imread.return_value = self.dummy_image

        # Mock the image processing functions
        mock_load_landmarks.return_value = self.dummy_features
        mock_create_mask.return_value = self.dummy_image
        mock_blur.return_value = self.dummy_image
        mock_resize_nose.return_value = self.dummy_image
        mock_augment_nose.return_value = self.dummy_image
        mock_augment_eabout:blank#blockedyes.return_value = self.dummy_image
        mock_imwrite.return_value = True

         # Run the function under test
        augment_image()

        # Get the arguments that augment_nose and augment_eyes were last called with
        nose_args, _ = mock_augment_nose.call_args
        eyes_args, _ = mock_augment_eyes.call_args

        # Verify that the image processing functions were called correctly
        self.assertEqual(type(nose_args[0]), str)
        self.assertTrue(np.array_equal(nose_args[1], self.dummy_features))
        self.assertEqual(nose_args[2], 1)

        self.assertEqual(type(eyes_args[0]), str)
        self.assertTrue(np.array_equal(eyes_args[1], self.dummy_features))
        self.assertEqual(eyes_args[2], 1)

        # Verify that the image was written to a file
        mock_imwrite.assert_called()

if __name__ == '__main__':
    unittest.main()