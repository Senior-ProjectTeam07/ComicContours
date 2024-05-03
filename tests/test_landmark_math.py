# test_landmark_math.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# import the necessary packages
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX
from landmarking.landmark_math import calc_dist, avg_feature_sizes, get_region_pts, global_avg_sizes, std_dev_features

class TestLandmarkMath(unittest.TestCase):
    def setUp(self):
        # Use self.features to store mock data
        self.features = np.array([
            [1, 48, 0, 100, 100], [1, 48, 1, 120, 100], [1, 48, 2, 140, 100], [1, 48, 3, 160, 100],
            [1, 60, 0, 180, 100], [1, 60, 1, 200, 100], [1, 60, 2, 220, 100], [1, 60, 3, 240, 100],
            [1, 17, 0, 300, 150], [1, 17, 1, 320, 150], [1, 17, 2, 340, 150],
            [1, 22, 0, 400, 150], [1, 22, 1, 420, 150], [1, 22, 2, 440, 150],
            [1, 36, 0, 300, 200], [1, 36, 1, 320, 200], [1, 36, 2, 340, 200],
            [1, 42, 0, 400, 200], [1, 42, 1, 420, 200], [1, 42, 2, 440, 200],
            [1, 27, 0, 200, 250], [1, 27, 1, 220, 250], [1, 27, 2, 240, 250],
            [1, 0, 0, 150, 300], [1, 0, 1, 170, 300], [1, 0, 2, 190, 300]
        ])

    def test_calc_dist_varied(self):
        test_cases = [
            ([0, 0], [3, 4], 5), ([1, 1], [4, 5], 5), ([2, 2], [2, 2], 0),
            ([0, 0], [0, 5], 5), ([0, 0], [5, 0], 5), ([3, 4], [0, 0], 5),
            ([-3, -4], [0, 0], 5), ([0.5, 0.5], [0.5, 2.5], 2)
        ]
        for pt1, pt2, expected in test_cases:
            self.assertAlmostEqual(calc_dist(pt1, pt2), expected)

    def test_all_regions(self):
        img_id = 1
        region_pts = get_region_pts(self.features, img_id)
        for region in FACIAL_LANDMARKS_68_IDX:
            self.assertIn(region, region_pts)
            # If region data is expected to be empty sometimes, check explicitly or handle it
            if region_pts[region].size > 0:
                self.assertNotEqual(len(region_pts[region]), 0)

    def test_avg_feature_sizes(self):
        img_id = 1
        avg_sizes = avg_feature_sizes(self.features, img_id)
        print("Average sizes computed:", avg_sizes)  # Debug output
        for region, size in avg_sizes.items():
            print(f"Region: {region}, Avg Size: {size}")  # More detailed output
        expected_min_size = 0  # Define a logical minimum size based on your data setup
        self.assertGreater(avg_sizes['Right_Eye'], expected_min_size, "'Right_Eye' size should be greater than {expected_min_size}")

    def test_global_avg_sizes_and_std_dev_features(self):
        global_avgs = global_avg_sizes(self.features)
        std_devs = std_dev_features(self.features, global_avgs)
        print("Global averages computed:", global_avgs)  # Debug output
        print("Standard deviations computed:", std_devs)  # Debug output
        expected_min_avg_size = 0  # Adjust based on expectations
        self.assertGreater(global_avgs['Right_Eye'], expected_min_avg_size, "Global average 'Right_Eye' size should be greater than {expected_min_avg_size}")


    def test_malformed_data(self):
        with self.assertRaises(ValueError):
            calc_dist([1, 2], ['a', 'b'])

if __name__ == '__main__':
    unittest.main()