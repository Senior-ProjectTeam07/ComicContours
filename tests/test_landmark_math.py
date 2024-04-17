# test_landmark_math.py

import unittest
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX
from landmarking.landmark_math import calc_dist, avg_feature_sizes, get_region_pts, global_avg_sizes, std_dev_features

class TestLandmarkMath(unittest.TestCase):
    def setUp(self):
        self.features = np.load(get_dir("data/facial_features.npy"))
        self.global_avgs = global_avg_sizes(self.features)
        self.std_devs = std_dev_features(self.features, self.global_avgs)

    def test_calc_dist(self):
        pt1 = [0, 0]
        pt2 = [3, 4]
        self.assertEqual(calc_dist(pt1, pt2), 5)

    def test_avg_feature_sizes(self):
        img_id = 0
        avg_sizes = avg_feature_sizes(self.features, img_id)
        self.assertTrue(isinstance(avg_sizes, dict))
        self.assertTrue(set(avg_sizes.keys()) == set(FACIAL_LANDMARKS_68_IDX.keys()))

    def test_get_region_pts(self):
        img_id = 0
        region_pts = get_region_pts(self.features, img_id)
        self.assertTrue(isinstance(region_pts, dict))
        self.assertTrue(set(region_pts.keys()) == set(FACIAL_LANDMARKS_68_IDX.keys()))

    def test_global_avg_sizes(self):
        self.assertTrue(isinstance(self.global_avgs, dict))
        self.assertTrue(set(self.global_avgs.keys()) == set(FACIAL_LANDMARKS_68_IDX.keys()))

    def test_std_dev_features(self):
        self.assertTrue(isinstance(self.std_devs, dict))
        self.assertTrue(set(self.std_devs.keys()) == set(FACIAL_LANDMARKS_68_IDX.keys()))

if __name__ == '__main__':
    unittest.main()