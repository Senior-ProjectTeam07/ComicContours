# test_landmark.py

import unittest
from unittest.mock import patch
import numpy as np
import cv2
import sys
import os
import io
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

    def test_valid_landmarks(self):
        for img_path in self.image_paths:
            landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
            if landmarks.size > 0:
                for landmark in landmarks:
                    feature = list(FACIAL_LANDMARKS_68_IDX.keys())[landmark[1]]
                    start, end = FACIAL_LANDMARKS_68_IDX[feature]
                    self.assertTrue(start <= landmark[2] < end)
                    self.assertTrue(0 <= landmark[3] < cv2.imread(img_path).shape[1])  # x-coordinate within image width
                    self.assertTrue(0 <= landmark[4] < cv2.imread(img_path).shape[0])  # y-coordinate within image height

    def test_csv_npy_contents(self):
        landmark()
        npy_file = np.load(get_dir('data/facial_features.npy'))
        csv_file = np.genfromtxt(get_dir('data/facial_features.csv'), delimiter=',', skip_header=1)
        self.assertTrue(np.array_equal(npy_file, csv_file))

    @patch('cv2.imread')
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_exception_handling(self, mock_stderr, mock_imread):
        mock_imread.return_value = None
        for img_path in self.image_paths:
            landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
            self.assertEqual(landmarks.size, 0)

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
        self.image_path_to_int[img_path] = max(self.image_path_to_int.values()) + 1  # add the test image path to the dictionary
        landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
        self.assertEqual(landmarks.size, 0)

    def test_image_with_multiple_faces(self):
        img_path = get_dir('data/test_images/multiple_faces.jpg')
        self.image_path_to_int[img_path] = max(self.image_path_to_int.values()) + 1  # add the test image path to the dictionary
        landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
        self.assertTrue(landmarks.size > 0)

    @patch('cv2.imread')
    def test_non_image_file(self, mock_imread):
        mock_imread.return_value = None
        img_path = get_dir('data/test_images/file.txt')
        self.image_path_to_int[img_path] = max(self.image_path_to_int.values()) + 1  # add the test image path to the dictionary
        landmarks = detect_format_landmarks(img_path, self.image_path_to_int, self.feature_to_int)
        self.assertEqual(landmarks.size, 0)
    
if __name__ == '__main__':
    unittest.main()