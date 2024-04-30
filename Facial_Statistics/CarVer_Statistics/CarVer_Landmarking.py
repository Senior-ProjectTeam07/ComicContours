# Author: Rhiannon Barber
# Landmarking system for CarVer dataset.

import dlib
import cv2
import numpy as np
import csv
from pathlib import Path

def get_dir(relative_path):
    base_dir = Path(__file__).resolve().parent
    return base_dir.joinpath(relative_path).resolve()

detector = dlib.get_frontal_face_detector()
predictor_path = str(get_dir("../shape_predictor_68_face_landmarks.dat"))
predictor = dlib.shape_predictor(predictor_path)

def read_demographics(file_path):  # reads the demographic file to extract the race and sex info, to add to arrays.
    demographics = {}
    with open(file_path, 'r') as file:
        next(file)
        for line in file:
            row = line.strip().split()
            if len(row) == 3:
                sub_folder_name, race, sex = row
                sub_folder_name = sub_folder_name.lower().replace('_', ' ')
                demographics[sub_folder_name] = {'race': race, 'sex': sex}
    return demographics

def process_image_to_array(image_path, image_path_to_int, feature_to_int, subfolder_id, subfolder_name, demographics, draw=False, output_path=None):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    all_features_array = []
    normalized_subfolder_name = subfolder_name.lower().replace('_', ' ')
    race, sex = demographics.get(normalized_subfolder_name, {'race': 'U', 'sex': 'U'}).values()
    for face in faces:
        landmarks = predictor(gray, face)
        if draw:
            draw_landmarks_and_save(img, landmarks, output_path)
        features = [  # all features are now to DLib standards. Separating eyes and eyebrows.
            ('jawline', range(0, 17)),
            ('left eyebrow', range(17, 22)), ('right eyebrow', range(22, 27)),
            ('left eye', range(36, 42)), ('right eye', range(42, 48)),
            ('nose', range(27, 36)), ('lips', range(48, 68))
        ]
        for feature_name, feature_index in features:
            for n in feature_index:
                x, y = landmarks.part(n).x, landmarks.part(n).y
                encoded_feature = [
                    subfolder_id, image_path_to_int[image_path],
                    feature_to_int[feature_name], n, x, y, race, sex
                ]
                all_features_array.append(encoded_feature)
    return np.array(all_features_array)

def draw_landmarks_and_save(img, landmarks, output_path):  # to draw the landmarks to see if properly placed.
    for n in range(0, 68):  # Assuming 68 landmarks
        x, y = landmarks.part(n).x, landmarks.part(n).y
        cv2.circle(img, (x, y), 1, (0, 255, 0), -1)
    cv2.imwrite(output_path, img)

def save_array_to_csv(array, file_name):  # this is so we can see visually how info is saved.
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Subfolder ID', 'Image ID', 'Feature', 'Landmark Index', 'X', 'Y', 'Race', 'Sex'])
        writer.writerows(array)
        print(f"CSV file has been updated successfully at {file_name}.")

def main():
    base_directory = get_dir('../CarVer_Data')
    output_base_directory = get_dir('')
    processed_images_base_directory = get_dir('processed_carver_photos')
    demographics_file_path = get_dir('CarVerDemographics.txt')
    demographics = read_demographics(demographics_file_path)
    subfolder_names = {}
    subfolder_id_counter = 0
    image_path_to_int = {}
    feature_to_int = {
        'jawline': 0, 'left eyebrow': 1, 'right eyebrow': 2,
        'left eye': 3, 'right eye': 4, 'nose': 5, 'lips': 6
    }
    all_features_list = []
    index = 0
    for image_path in sorted(base_directory.rglob('*.[pj][np]g')):
        subfolder_name = image_path.parent.name
        if subfolder_name not in subfolder_names:
            subfolder_names[subfolder_name] = subfolder_id_counter
            subfolder_id_counter += 1
        subfolder_id = subfolder_names[subfolder_name]
        image_path_to_int[str(image_path)] = index
        subfolder_path = processed_images_base_directory.joinpath(subfolder_name)
        subfolder_path.mkdir(parents=True, exist_ok=True)
        output_image_path = subfolder_path.joinpath(f'{subfolder_name}_{index}.jpg')
        features_array = process_image_to_array(str(image_path), image_path_to_int, feature_to_int, subfolder_id, subfolder_name, demographics, True, str(output_image_path))
        if features_array.size > 0:
            all_features_list.append(features_array)
        index += 1
    if all_features_list:
        all_features = np.vstack(all_features_list) # I used vstack because of errors I was getting otherwise.
                                                    # This can be changed if needed.
        npy_file_path = str(output_base_directory.joinpath('carver_features.npy'))
        np.save(npy_file_path, all_features)
        save_array_to_csv(all_features, str(output_base_directory.joinpath('carver_features.csv')))
    else:
        print("No landmark data was saved due to lack of detected features.")

if __name__ == "__main__":
    main()
