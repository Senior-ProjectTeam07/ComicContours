# test_landmark_utils.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
import unittest
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int

class TestLandmarkUtils(unittest.TestCase):
    def test_facial_landmarks_68_idx(self):
        # Verify that the dictionary contains the correct keys
        self.assertEqual(set(FACIAL_LANDMARKS_68_IDX.keys()), set(["Outer_Lip", "Inner_Lip", "Right_Eyebrow", "Left_Eyebrow", "Right_Eye", "Left_Eye", "Nose", "Jaw"]))

        # Verify that the dictionary contains the correct values
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Outer_Lip"], (48, 60))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Inner_Lip"], (60, 68))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Right_Eyebrow"], (17, 22))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Left_Eyebrow"], (22, 27))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Right_Eye"], (36, 42))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Left_Eye"], (42, 48))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Nose"], (27, 36))
        self.assertEqual(FACIAL_LANDMARKS_68_IDX["Jaw"], (0, 17))

    def test_feature_to_int(self):
        # Verify that the dictionary contains the correct keys
        self.assertEqual(set(feature_to_int.keys()), set(["Outer_Lip", "Inner_Lip", "Right_Eyebrow", "Left_Eyebrow", "Right_Eye", "Left_Eye", "Nose", "Jaw"]))

        # Verify that the dictionary contains the correct values
        self.assertEqual(feature_to_int["Outer_Lip"], 0)
        self.assertEqual(feature_to_int["Inner_Lip"], 1)
        self.assertEqual(feature_to_int["Right_Eyebrow"], 2)
        self.assertEqual(feature_to_int["Left_Eyebrow"], 3)
        self.assertEqual(feature_to_int["Right_Eye"], 4)
        self.assertEqual(feature_to_int["Left_Eye"], 5)
        self.assertEqual(feature_to_int["Nose"], 6)
        self.assertEqual(feature_to_int["Jaw"], 7)

if __name__ == '__main__':
    unittest.main()