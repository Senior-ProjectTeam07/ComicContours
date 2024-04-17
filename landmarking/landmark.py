# landmarking.py

# import the necessary packages
import dlib
import cv2
import numpy as np
import csv
import sys
import os
from multiprocessing import Pool

# Ensure the current and parent directories are in the path for module imports
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int
from landmarking.landmarks_to_style import LandmarksToStyle, LandmarksStyleDataset, create_dataloader

# Attempt to load the dlib face detector and shape predictor, handling any initialization errors
detector = dlib.get_frontal_face_detector()
predictor_path = get_dir("landmarking/shape_predictor_68_face_landmarks.dat")
try:
    predictor = dlib.shape_predictor(predictor_path)
except Exception as e:
    sys.exit(f"Failed to load dlib shape predictor: {str(e)}")

def detect_format_landmarks(image_path, image_path_to_int, feature_to_int):
    # Validate and handle errors for the input image path
    if not os.path.exists(image_path):
        print(f"Image {image_path} does not exist. Skipping.")
        return np.array([])
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image at {image_path}.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return np.array([])

    faces = detector(gray)
    all_features_array = []
    for face in faces:
        landmarks = predictor(gray, face)
        for feature_name, feature_range in FACIAL_LANDMARKS_68_IDX.items():
            for n in range(*feature_range):
                x, y = landmarks.part(n).x, landmarks.part(n).y
                encoded_feature = [image_path_to_int[image_path], feature_to_int[feature_name], n, x, y]
                all_features_array.append(encoded_feature)
    
    return np.array(all_features_array)

def draw_landmarks_and_save(image_path, landmarks, output_directory):
    try:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}.")
        
        for landmark in landmarks:
            x, y = int(landmark[3]), int(landmark[4])
            cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
        base_filename = os.path.basename(image_path)
        processed_filename = f"Processed_{base_filename}"
        output_path = os.path.join(output_directory, processed_filename)
        cv2.imwrite(output_path, img)
    except Exception as e:
        print(f"Error while drawing landmarks for {image_path}: {e}")

def save_array_to_csv(array, file_name):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Image ID', 'Feature', 'Landmark Index', 'X', 'Y'])
        writer.writerows(array)

def landmarking_process(image_path, image_path_to_int, feature_to_int, output_directory):
    landmarks = detect_format_landmarks(image_path, image_path_to_int, feature_to_int)
    if landmarks.size > 0:
        draw_landmarks_and_save(image_path, landmarks, output_directory)
    return landmarks

def landmark():
    image_directory = get_dir('data/original_images')
    output_directory = get_dir('data/processed_images')
    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory)
                   if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_paths:
        print("No images found in the specified directory.")
        return
    
    image_path_to_int = {path: idx for idx, path in enumerate(image_paths)}

    # Using multiprocessing for performance optimization
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(landmarking_process, [(path, image_path_to_int, feature_to_int, output_directory) for path in image_paths])

    all_features = np.vstack([res for res in results if res.size > 0])
    if all_features.size == 0:
        print("No facial features detected in any of the images.")
        return
    
    np.save(get_dir('data/facial_features.npy'), all_features)
    save_array_to_csv(all_features, get_dir('data/facial_features.csv'))

    print("Success: The landmarkings have been saved to a NumPy array and CSV file.")

def landmarking_process_style(image_path, image_path_to_int, feature_to_int, output_directory):
    landmarks = detect_format_landmarks(image_path, image_path_to_int, feature_to_int)
    if landmarks.size > 0:
        draw_landmarks_and_save(image_path, landmarks, output_directory)
    
    # Convert landmarks to style vectors
    num_landmarks = 68
    style_dim = 512
    model = LandmarksToStyle(num_landmarks, style_dim)
    style_vectors = model(landmarks)
    
    return style_vectors

def landmark_style():
    image_directory = get_dir('data/original_images')
    output_directory = get_dir('data/processed_images')
    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory)
                   if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_paths:
        print("No images found in the specified directory.")
        return
    
    image_path_to_int = {path: idx for idx, path in enumerate(image_paths)}

    # Using multiprocessing for performance optimization
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(landmarking_process_style, [(path, image_path_to_int, feature_to_int, output_directory) for path in image_paths])

    all_features = np.vstack([res for res in results if res.size > 0])
    if all_features.size == 0:
        print("No facial features detected in any of the images.")
        return
    
    np.save(get_dir('data/facial_features.npy'), all_features)
    save_array_to_csv(all_features, get_dir('data/facial_features.csv'))

    # Create the dataset and dataloader
    dataset = LandmarksStyleDataset(loaded_landmarks, 'path/to/images', transform=transform)
    dataloader = create_dataloader(dataset, batch_size=4, shuffle=True)

    # Sample training loop for one epoch
    for data in dataloader:
        landmarks, images = data['landmarks'], data['image']
        style_vectors = mapping_network(landmarks)
        # Now use `style_vectors` and `images` for StyleCariGAN training

    print("Success: The landmarkings have been saved to a NumPy array and CSV file.")