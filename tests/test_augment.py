# test_augment.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import unittest
import numpy as np
import cv2
from augmentation.augment import augment_image, augment_nose, augment_eyes, augment_mouth, get_std_dev_feature
from utils.file_utils import get_dir
from utils.landmark_utils import feature_to_int, int_to_feature

class TestAugment(unittest.TestCase):
    def setUp(self):
        self.facial_features = np.load(get_dir('data/facial_features.npy'))
        self.feature_to_int = feature_to_int
        self.image_directory = get_dir('data/original_images')
        self.augmented_directory = get_dir('data/augmented_images')
        self.nose_scale_factor = 1.25
        self.image_paths = [os.path.join(self.image_directory, filename) for filename in os.listdir(self.image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def test_get_std_dev_feature(self):
        for img_path in self.image_paths:
            image_id = self.image_paths.index(img_path)
            try:
                nose_std, mouth_std, eyes_std, nose_avg, mouth_avg, eyes_avg = get_std_dev_feature(image_id)
                self.assertIsNotNone(nose_std)
                self.assertIsNotNone(mouth_std)
                self.assertIsNotNone(eyes_std)
                self.assertIsNotNone(nose_avg)
                self.assertIsNotNone(mouth_avg)
                self.assertIsNotNone(eyes_avg)
            except ValueError as e:
                self.fail(f"Test failed with ValueError: {e}")

    def test_augment_eyes(self):
        eyes_scale_factor = 1.25
        for img_path in self.image_paths:
            image_id = self.image_paths.index(img_path)
            try:
                img = cv2.imread(img_path)
                augmented_img = augment_eyes(img, self.facial_features, image_id, self.feature_to_int, eyes_scale_factor)
                self.assertIsNotNone(augmented_img)
                self.assertEqual(augmented_img.shape, img.shape)
                self.assertEqual(augmented_img.dtype, img.dtype)
            except ValueError as e:
                self.fail(f"Test failed with ValueError: {e}")

    def test_augment_nose(self):
        for img_path in self.image_paths:
            image_id = self.image_paths.index(img_path)
            try:
                augmented_img = augment_nose(img_path, self.facial_features, image_id, self.feature_to_int, self.nose_scale_factor)
                img = cv2.imread(img_path)
                self.assertIsNotNone(augmented_img)
                self.assertEqual(augmented_img.shape, img.shape)
                self.assertEqual(augmented_img.dtype, img.dtype)
            except ValueError as e:
                self.fail(f"Test failed with ValueError: {e}")

    def test_augment_mouth(self):
        mouth_scale_factor = 1.25
        for img_path in self.image_paths:
            image_id = self.image_paths.index(img_path)
            try:
                img = cv2.imread(img_path)
                original_img = img.copy()
                augmented_img = augment_mouth(img, original_img, self.facial_features, image_id, self.feature_to_int, mouth_scale_factor)
                self.assertIsNotNone(augmented_img)
                self.assertEqual(augmented_img.shape, img.shape)
                self.assertEqual(augmented_img.dtype, img.dtype)
            except ValueError as e:
                self.fail(f"Test failed with ValueError: {e}")

    def test_augment_image(self):
        initial_files = set(os.listdir(self.augmented_directory))
        try:
            augment_image()
            augmented_images = set(os.listdir(self.augmented_directory))
            new_files = augmented_images - initial_files
            self.assertTrue(len(new_files) > 0)
            for filename in new_files:
                img = cv2.imread(os.path.join(self.augmented_directory, filename))
                self.assertIsNotNone(img)
        except ValueError as e:
            self.fail(f"Test failed with ValueError: {e}")

if __name__ == '__main__':
    unittest.main()