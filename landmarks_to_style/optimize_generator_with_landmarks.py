# optimize_generator_with_landmarks.py



from StyleCariGAN.model import Generator
from StyleCariGAN.train import train
from landmarking.load import load_feature_landmarks
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX
from utils.file_utils import get_dir

def optimize_generator_with_landmarks():
    # Create an instance of LandmarksToStyle
    num_landmarks = 68
    style_dim = 512
    model = LandmarksToStyle(num_landmarks, style_dim)

    # Convert landmarks to style vectors
    style_vectors = model(landmarks)

