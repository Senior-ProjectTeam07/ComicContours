import dlib
import cv2
import os
import numpy as np
import csv

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("Augmentation_Project/shape_predictor_68_face_landmarks.dat")


def process_image_to_array(image_path, image_path_to_int, feature_to_int):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    all_features_array = []
    for face in faces:
        landmarks = predictor(gray, face)
        for feature_name, feature_index in [('jawline', range(17)), ('eyebrows', range(17, 27)), ('nose', range(27, 36)), ('eyes', range(36, 48)), ('lips', range(48, 68))]:
            for n in feature_index:
                x, y = landmarks.part(n).x, landmarks.part(n).y
                encoded_feature = [image_path_to_int[image_path], feature_to_int[feature_name], n, x, y]
                all_features_array.append(encoded_feature)
    return np.array(all_features_array)


def draw_landmarks_and_save(image_path, landmarks, output_directory):
    img = cv2.imread(image_path)
    for landmark in landmarks:
        x, y = landmark[3], landmark[4]
        cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
    base_filename = os.path.basename(image_path)
    processed_filename = f"Processed_{base_filename}"
    output_path = os.path.join(output_directory, processed_filename)
    cv2.imwrite(output_path, img)


def save_array_to_csv(array, file_name):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Image ID', 'Feature', 'Landmark Index', 'X', 'Y'])
        writer.writerows(array)


def main():
    if not os.path.exists('Augmentation_Project/processed_images'):
        os.makedirs('Augmentation_Project/processed_images')

    image_directory = 'Augmentation_Project/original_images'
    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_path_to_int = {path: idx for idx, path in enumerate(image_paths)}
    feature_to_int = {'jawline': 0, 'eyebrows': 1, 'nose': 2, 'eyes': 3, 'lips': 4}
    all_features_list = []

    for path in image_paths:
        features_array = process_image_to_array(path, image_path_to_int, feature_to_int)
        all_features_list.append(features_array)

    all_features = np.vstack(all_features_list)
    np.save('Augmentation_Project/facial_features.npy', all_features)

    save_array_to_csv(all_features, 'Augmentation_Project/facial_features.csv')

    output_directory = 'Augmentation_Project/processed_images'
    for path in image_paths:
        current_image_landmarks = all_features[all_features[:, 0] == image_path_to_int[path]]
        draw_landmarks_and_save(path, current_image_landmarks, output_directory)

    print("Success.")
    print("The landmarkings have been saved to a NumPy array, and facial_features.npy ")
    print("For double checking, the array data was also saved to facial_features.csv ")


if __name__ == "__main__":
    main()
