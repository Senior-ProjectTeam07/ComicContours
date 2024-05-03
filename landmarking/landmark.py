# landmarking.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# import the necessary packages
import dlib
import cv2
import numpy as np
import csv
import logging
from PIL import Image
from multiprocessing import Pool
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int, int_to_feature

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s:%(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler('landmarking.log'),
        logging.StreamHandler()
    ]
)

# Attempt to load the dlib face detector and shape predictor, handling any initialization errors
detector = dlib.get_frontal_face_detector()
predictor_path = get_dir("landmarking/shape_predictor_68_face_landmarks.dat")
try:
    predictor = dlib.shape_predictor(predictor_path)
except Exception as e:
    logging.critical(f"Failed to load dlib shape predictor: {str(e)}")
    sys.exit(1)

def validate_features(features_array):
    """
    Validates the features in the numpy array against the int_to_feature dictionary.
    """
    # Get the unique feature names from the numpy array
    unique_feature_names = np.unique(features_array[:, 1])

    # Check if all feature names are in the int_to_feature dictionary
    for feature_name in unique_feature_names:
        if feature_name not in int_to_feature.keys():
            logging.error(f"Invalid feature name {feature_name} found in the numpy array.")
            return False

    logging.info("All features in the numpy array are valid.")
    return True

def get_image_format(image_path):
    try:
        with Image.open(image_path) as img:
            return img.format.lower()
    except Exception as e:
        logging.error(f"Failed to open image {image_path}: {str(e)}")
        return None

def detect_format_landmarks(image_path, image_path_to_int, feature_to_int):
    """
    Detects and formats landmarks for a given image.
    """
    if not os.path.exists(image_path):
        logging.error(f"Image {image_path} does not exist. Skipping.")
        return np.array([])
    
    image_format = get_image_format(image_path)
    if image_format not in ['jpg', 'jpeg', 'png', 'tiff']:
        logging.error(f"Unsupported image format {image_format} for image {image_path}. Skipping.")
        return np.array([])
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image at {image_path}.")
        
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return np.array([])

    faces = detector(gray)
    if not faces:
        logging.info(f"No faces found in image {image_path}. Skipping.")
        return np.array([])
    
    all_features_array = []
    for face in faces:
        landmarks = predictor(gray, face)
        for feature_name, feature_range in FACIAL_LANDMARKS_68_IDX.items():
            if feature_name not in feature_to_int:
                logging.error(f"Feature name {feature_name} not found in feature_to_int dictionary.")
                continue
            for n in range(*feature_range):
                x, y = landmarks.part(n).x, landmarks.part(n).y
                encoded_feature = [image_path_to_int[image_path], feature_to_int[feature_name], n, x, y]
                all_features_array.append(encoded_feature)
    
    return np.array(all_features_array)

def draw_landmarks_and_save(image_path, landmarks, output_directory):
    """
    Draws landmarks on images and saves them to specified directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}.")
        
        for landmark in landmarks:
            cv2.circle(img, (int(landmark[3]), int(landmark[4])), 3, (0, 255, 0), -1)
        
        processed_filename = f"Processed_{os.path.basename(image_path)}"
        cv2.imwrite(os.path.join(output_directory, processed_filename), img)
    except Exception as e:
        logging.error(f"Error while drawing landmarks for {image_path}: {str(e)}")

def save_array_to_csv(array, file_name):
    """
    Validates the features and saves a numpy array to a CSV file.
    """
    if not validate_features(array):
        logging.error("Failed to save the numpy array due to invalid features.")
        return

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Image ID', 'Feature', 'Landmark Index', 'X', 'Y'])
        writer.writerows(array)

def write_pts_file(landmarks, image_path):
    """
    Writes landmark points to a .pts file.
    """
    pts_filename = os.path.splitext(image_path)[0] + '.pts'
    with open(pts_filename, 'w') as f:
        f.write("version: 1\n")
        f.write(f"n_points: {len(landmarks)}\n")
        f.write("{\n")
        for landmark in landmarks:
            f.write(f"{int(landmark[3])} {int(landmark[4])}\n")
        f.write("}\n")

def landmarking_process(image_path, image_path_to_int, feature_to_int, output_directory):
    """
    Process landmark detection, drawing, and saving for a single image.
    """
    landmarks = detect_format_landmarks(image_path, image_path_to_int, feature_to_int)
    if landmarks.size > 0:
        draw_landmarks_and_save(image_path, landmarks, output_directory)
        write_pts_file(landmarks, image_path)
    return landmarks

def landmark():
    image_directory = get_dir('data/original_images')
    output_directory = get_dir('data/processed_images')
    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory)
                   if filename.lower().endswith(('jpg', 'jpeg', 'png', 'tiff'))]

    if not image_paths:
        logging.info("No images found in the specified directory.")
        return
    
    image_path_to_int = {path: idx for idx, path in enumerate(image_paths)}

    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(landmarking_process, [(path, image_path_to_int, feature_to_int, output_directory) for path in image_paths])

    all_features = np.vstack([res for res in results if res.size > 0])
    if all_features.size == 0:
        logging.info("No facial features detected in any of the images.")
        return
    
    np.save(get_dir('data/facial_features.npy'), all_features)
    save_array_to_csv(all_features, get_dir('data/facial_features.csv'))

    if not check_csv_accuracy(get_dir('data/facial_features.csv'), all_features):
        logging.error("Failed to verify the accuracy of the data in the CSV file.")

    logging.info("Success: The landmarkings have been saved to a NumPy array and CSV file.")

def check_csv_accuracy(csv_file, original_array):
    """
    Checks the accuracy of the data saved in the CSV file against the original numpy array.
    """
    # Load the data from the CSV file
    csv_data = np.genfromtxt(csv_file, delimiter=',', skip_header=1)

    # Check if the shapes of the two arrays are the same
    if csv_data.shape != original_array.shape:
        logging.error("The shapes of the CSV data and the original numpy array do not match.")
        return False

    # Check if the data in the two arrays are the same
    if not np.allclose(csv_data, original_array):
        logging.error("The data in the CSV file and the original numpy array do not match.")
        return False

    logging.info("The data in the CSV file is accurate.")
    return True

if __name__ == "__main__":
    landmark()