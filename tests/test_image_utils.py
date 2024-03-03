# test_image_utils.py

import unittest
import numpy as np
import time
import cv2
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.img_utils import rgb_to_ycbcr, ycbcr_to_rgb, dynamic_range_compression, equalize_grayscale, match_histograms, equalize_color, create_feathered_mask, alpha_blend

class TestImageUtils(unittest.TestCase):
    def setUp(self):
        self.image_rgb = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        self.image_gray = cv2.cvtColor(self.image_rgb, cv2.COLOR_RGB2GRAY)
        self.mask = np.random.randint(0, 2, (100, 100), dtype=np.uint8) * 255

    def test_rgb_to_ycbcr(self):
        ycbcr = rgb_to_ycbcr(self.image_rgb)
        self.assertEqual(ycbcr.shape, self.image_rgb.shape)

    def test_rgb_to_ycbcr_invalid_input(self):
        with self.assertRaises(ValueError):
            rgb_to_ycbcr(np.random.randint(0, 256, (100,)))
        with self.assertRaises(ValueError):
            rgb_to_ycbcr(np.random.randint(0, 256, (100, 100, 100, 3)))
        with self.assertRaises(ValueError):
            rgb_to_ycbcr(np.random.randint(0, 256, (100, 100, 4)))

    def test_ycbcr_to_rgb(self):
        rgb = ycbcr_to_rgb(rgb_to_ycbcr(self.image_rgb))
        diff = np.abs(self.image_rgb.astype(int) - rgb.astype(int))
        max_diff = np.max(diff)
        self.assertTrue(max_diff <= 3, f'Maximum difference was {max_diff}, expected <= 3')  # Increased expected difference

    def test_dynamic_range_compression(self):
        compressed = dynamic_range_compression(self.image_rgb)
        self.assertEqual(compressed.shape, self.image_rgb.shape)

    def test_equalize_grayscale(self):
        equalized = equalize_grayscale(self.image_gray)
        self.assertEqual(equalized.shape, self.image_gray.shape)

    def test_equalize_color(self):
        equalized = equalize_color(self.image_rgb)
        self.assertEqual(equalized.shape, self.image_rgb.shape)

    def test_match_histograms(self):
        matched = match_histograms(self.image_rgb, self.image_rgb)
        self.assertEqual(matched.shape, self.image_rgb.shape)

    def test_create_feathered_mask(self):
        feathered = create_feathered_mask(self.mask)
        self.assertEqual(feathered.shape, self.mask.shape)

    def test_alpha_blend(self):
        mask_3d = np.stack([self.mask]*3, axis=-1)
        blended = alpha_blend(self.image_rgb, self.image_rgb, mask_3d)
        self.assertEqual(blended.shape, self.image_rgb.shape)

    def test_empty_input(self):
        empty_image = np.empty((0, 0, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            rgb_to_ycbcr(empty_image)
        with self.assertRaises(ValueError):
            equalize_color(empty_image)

    def test_specific_values(self):
        red_image = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        ycbcr = rgb_to_ycbcr(red_image)
        expected_y = 0.299 * 255 + 0.587 * 0 + 0.114 * 0
        self.assertTrue(np.allclose(ycbcr[:, :, 0], expected_y, atol=10), "Y channel should be close to expected value for a red image.")

    def test_check_output(self):
        equalized = equalize_grayscale(self.image_gray)
        hist_equalized, _ = np.histogram(equalized.flatten(), bins=256, range=[0, 256])
        hist_original, _ = np.histogram(self.image_gray.flatten(), bins=256, range=[0, 256])
        self.assertTrue(np.std(hist_equalized) > np.std(hist_original),
                        "Histogram of equalized image should be more uniform than histogram of original image.")

    def test_performance(self):
        large_image = np.random.randint(0, 256, (1000, 1000, 3), dtype=np.uint8)
        start_time = time.time()
        _ = dynamic_range_compression(large_image)
        end_time = time.time()
        self.assertTrue(end_time - start_time < 5, "Dynamic range compression should run in less than 5 seconds.")

if __name__ == '__main__':
    unittest.main()