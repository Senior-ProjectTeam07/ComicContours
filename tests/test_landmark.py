# test_landmark.py

import unittest
from unittest.mock import patch, ANY
import numpy as np
import cv2
import sys
import os
import logging
from io import StringIO

# Ensure the correct import paths
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from landmarking.landmark import detect_format_landmarks, draw_landmarks_and_save, landmarking_process, landmark
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX

class TestLandmark(unittest.TestCase):
    def setUp(self):
        self.image_directory = get_dir('data/original_images')
        self.output_directory = get_dir('data/processed_images')
        self.image_paths = [os.path.join(self.image_directory, filename) for filename in os.listdir(self.image_directory)
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.image_path_to_int = {path: idx for idx, path in enumerate(self.image_paths)}
        self.feature_to_int = {feature: idx for idx, feature in enumerate(FACIAL_LANDMARKS_68_IDX.keys())}
        self.image_cache = {}

    def test_detect_format_landmarks(self):
        for img_path in self.image_paths:
            landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
            self.assertIsNotNone(landmarks)

    def test_draw_landmarks_and_save(self):
        for img_path in self.image_paths:
            landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
            if landmarks.size > 0:
                draw_landmarks_and_save(img_path, landmarks, self.output_directory)
                base_filename = os.path.basename(img_path)
                processed_filename = f"Processed_{base_filename}"
                output_path = os.path.join(self.output_directory, processed_filename)
                self.assertTrue(os.path.exists(output_path))
                self.assertGreater(os.path.getsize(output_path), 0, "Output file should not be empty")

    def test_valid_landmarks(self):
        for img_path in self.image_paths:
            landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
            if landmarks.size > 0:
                img = self.get_image(img_path)
                for landmark in landmarks:
                    feature = list(FACIAL_LANDMARKS_68_IDX.keys())[landmark[1]]
                    start, end = FACIAL_LANDMARKS_68_IDX[feature]
                    self.assertTrue(start <= landmark[2] < end)
                    self.assertTrue(0 <= landmark[3] < img.shape[1])  # x-coordinate within image width
                    self.assertTrue(0 <= landmark[4] < img.shape[0])  # y-coordinate within image height

    def test_csv_npy_contents(self):
        landmark()
        npy_file = np.load(get_dir('data/facial_features.npy'))
        csv_file = np.genfromtxt(get_dir('data/facial_features.csv'), delimiter=',', skip_header=1)
        self.assertTrue(np.allclose(npy_file, csv_file, atol=1e-6), "Numpy array and CSV content should be equivalent.")

    @patch('cv2.imread')
    @patch('logging.error')
    def test_exception_handling(self, mock_error, mock_imread):
        mock_imread.return_value = None  # Simulate cv2.imread returning None
        for img_path in self.image_paths:
            with self.subTest(img_path=img_path):
                detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
                mock_error.assert_called_with(ANY, img_path, ANY)
                mock_error.reset_mock()

    def test_landmarking_process(self):
        for img_path in self.image_paths:
            landmarks = landmarking_process(img_path, self.image_path_to_int, self.feature_to_int, self.output_directory)
            self.assertIsNotNone(landmarks)

    def test_landmark(self):
        landmark()
        self.assertTrue(os.path.exists(get_dir('data/facial_features.npy')))
        self.assertTrue(os.path.exists(get_dir('data/facial_features.csv')))

    def test_image_without_landmarks(self):
        img_path = get_dir('data/test_images/no_face.jpg')
        self.image_path_to_int[img_path] = max(self.image_path_to_int.values()) + 1
        landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
        self.assertEqual(landmarks.size, 0)

    def test_image_with_multiple_faces(self):
        img_path = get_dir('data/test_images/multiple_faces.jpg')
        self.image_path_to_int[img_path] = max(self.image_path_to_int.values()) + 1
        landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
        self.assertTrue(landmarks.size > 0)

    @patch('cv2.imread')
    def test_non_image_file(self, mock_imread):
        mock_imread.return_value = None
        img_path = get_dir('data/test_images/file.txt')
        self.image_path_to_int[img_path] = max(self.image_path_to_int.values()) + 1
        landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
        self.assertEqual(landmarks.size, 0)

    def get_image(self, img_path):
        if img_path not in self.image_cache:
            self.image_cache[img_path] = cv2.imread(img_path)
        return self.image_cache[img_path]

if __name__ == "__main__":
    unittest.main()