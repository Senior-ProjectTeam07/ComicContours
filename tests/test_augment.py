import unittest
import numpy as np
import cv2
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.augment import augment_image, augment_nose, augment_eyes
from utils.file_utils import get_dir
from utils.landmark_utils import feature_to_int

class TestAugment(unittest.TestCase):
    def setUp(self):
        self.facial_features = np.load(get_dir('data/facial_features.npy'))
        self.feature_to_int = feature_to_int
        self.image_directory = get_dir('data/original_images')
        self.augmented_directory = get_dir('data/augmented_images')
        self.nose_scale_factor = 1.25
        self.image_paths = [os.path.join(self.image_directory, filename) for filename in os.listdir(self.image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def test_augment_nose(self):
        for img_path in self.image_paths:
            image_id = self.image_paths.index(img_path)
            img = cv2.imread(img_path)
            augmented_img = augment_nose(img_path, self.facial_features, image_id, self.feature_to_int, self.nose_scale_factor)
            self.assertIsNotNone(augmented_img)

    def test_augment_eyes(self):
        eyes_scale_factor = 1.25
        for img_path in self.image_paths:
            image_id = self.image_paths.index(img_path)
            augmented_img = augment_eyes(img_path, self.facial_features, image_id, self.feature_to_int, eyes_scale_factor)  # Pass img_path instead of img
            self.assertIsNotNone(augmented_img)

    def test_augment_image(self):
        augment_image()
        augmented_images = os.listdir(self.augmented_directory)
        self.assertTrue(len(augmented_images) > 0)

if __name__ == '__main__':
    unittest.main()