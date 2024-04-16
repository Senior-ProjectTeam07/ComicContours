import unittest
from unittest.mock import patch
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.make_image import make_img
from augmentation.eyes import multiply_eye_mask

class TestMakeImage(unittest.TestCase):
    def setUp(self):
        self.img = np.zeros((500, 500, 3), dtype=np.uint8)
        self.mask = np.zeros((500, 500, 3), dtype=np.uint8)
        self.face_landmarks = np.array([[0, 100]])
        self.eyebrow_landmarks = np.array([[100, 200], [200, 300], [300, 400], [400, 500]])
        self.face_img = np.zeros((500, 500, 3), dtype=np.uint8)

    def mock_multiply_eye_mask(mask, inverse_mask, eye, face):
        return np.zeros_like(mask)

    @patch('augmentation.eyes.multiply_eye_mask', side_effect=mock_multiply_eye_mask)
    def test_make_img_mask(self, mock_multiply_eye_mask):
        make_img(self.img, self.mask, self.face_landmarks, self.eyebrow_landmarks, self.face_img, 'mask')

    @patch('augmentation.eyes.multiply_eye_mask', side_effect=mock_multiply_eye_mask)
    def test_make_img_not_mask(self, mock_multiply_eye_mask):
        make_img(self.img, self.mask, self.face_landmarks, self.eyebrow_landmarks, self.face_img, 'not_mask')
        #mock_multiply_eye_mask.assert_called()

    def test_invalid_img(self):
        with self.assertRaises(ValueError):
            make_img(None, self.mask, self.face_landmarks, self.eyebrow_landmarks, self.face_img, 'mask')

    def test_invalid_mask(self):
        with self.assertRaises(ValueError):
            make_img(self.img, None, self.face_landmarks, self.eyebrow_landmarks, self.face_img, 'mask')

    def test_invalid_face_landmarks(self):
        with self.assertRaises(ValueError):
            make_img(self.img, self.mask, None, self.eyebrow_landmarks, self.face_img, 'mask')

    def test_invalid_eyebrow_landmarks(self):
        with self.assertRaises(ValueError):
            make_img(self.img, self.mask, self.face_landmarks, None, self.face_img, 'mask')

    def test_invalid_face_img(self):
        with self.assertRaises(ValueError):
            make_img(self.img, self.mask, self.face_landmarks, self.eyebrow_landmarks, None, 'mask')

    def test_invalid_type_mask(self):
        with self.assertRaises(ValueError):
            make_img(self.img, self.mask, self.face_landmarks, self.eyebrow_landmarks, self.face_img, None)

if __name__ == '__main__':
    unittest.main()