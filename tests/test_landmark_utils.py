# test_landmark_utils.py

import unittest
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int

class TestLandmarkUtils(unittest.TestCase):
    def test_facial_landmarks_68_idx(self):
        # Verify that the dictionary contains the correct keys
        self.assertEqual(set(FACIAL_LANDMARKS_68_IDX.keys()), set(["Mouth", "Right_Eyebrow", "Left_Eyebrow", "Right_Eye", "Left_Eye", "Nose", "Jaw"]))

        # Verify that the dictionary contains the correct values
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Mouth"], (48, 68))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Right_Eyebrow"], (17, 22))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Left_Eyebrow"], (22, 27))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Right_Eye"], (36, 42))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Left_Eye"], (42, 48))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Nose"], (27, 35))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Jaw"], (0, 17))

    def test_feature_to_int(self):
        # Verify that the dictionary contains the correct keys
        self.assertEqual(set(feature_to_int.keys()), set(["Mouth", "Right_Eyebrow", "Left_Eyebrow", "Right_Eye", "Left_Eye", "Nose", "Jaw"]))

        # Verify that the dictionary contains the correct values
        self.assertEqual(feature_to_int["Mouth"], 0)
        self.assertEqual(feature_to_int["Right_Eyebrow"], 1)
        self.assertEqual(feature_to_int["Left_Eyebrow"], 2)
        self.assertEqual(feature_to_int["Right_Eye"], 3)
        self.assertEqual(feature_to_int["Left_Eye"], 4)
        self.assertEqual(feature_to_int["Nose"], 5)
        self.assertEqual(feature_to_int["Jaw"], 6)

if __name__ == '__main__':
    unittest.main()