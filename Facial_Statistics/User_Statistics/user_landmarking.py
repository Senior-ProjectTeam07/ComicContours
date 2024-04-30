# author: Rhiannon Barber
# This file landmarks the facial regions of a user photo.
# The image is resized to the size that the CarVer photos are, so that
# when the stats analysis is done, the deviation isn't skewed because of the size of the img.

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

# had to resize the image, otherwise the deviations from any photo not this size was extremely large.
def resize_image(image, target_size=(178, 218)):
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    return resized_image

def process_image_to_array(image_path, image_id, save_directory):
    img = cv2.imread(str(image_path))
    img = resize_image(img)  # Resize the image to the target size
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    all_features_array = []
    features = {
        'jawline': 0, 'left eyebrow': 1, 'right eyebrow': 2,
        'left eye': 3, 'right eye': 4, 'nose': 5, 'lips': 6
    }
    for face in faces:
        landmarks = predictor(gray, face)
        for feature_name, feature_code in features.items():
            indices = {
                'jawline': range(0, 17), 'left eyebrow': range(17, 22),
                'right eyebrow': range(22, 27), 'left eye': range(36, 42),
                'right eye': range(42, 48), 'nose': range(27, 36), 'lips': range(48, 68)
            }[feature_name]
            for n in indices:
                x, y = landmarks.part(n).x, landmarks.part(n).y
                cv2.circle(img, (x, y), 1, (0, 255, 0), -1)
                all_features_array.append([image_id, feature_code, n, x, y])
    processed_image_path = save_directory / f"processed_{image_path.name}"
    cv2.imwrite(str(processed_image_path), img)
    return np.array(all_features_array)

def main():
    user_photos_directory = get_dir('user_photos')
    processed_photos_directory = get_dir('processed_user_photos')
    processed_photos_directory.mkdir(exist_ok=True)
    all_features_list = []
    image_id = 0
    # the logic is sorted because of the CarVer set, I don't think its necessary for the user, but I kept it just
    # in case.
    for image_path in sorted(user_photos_directory.glob('*.jpg')) + sorted(user_photos_directory.glob('*.jpeg')) + sorted(user_photos_directory.glob('*.png')):
        features_array = process_image_to_array(image_path, image_id, processed_photos_directory)
        if features_array.size > 0:
            all_features_list.append(features_array)
        image_id += 1
    if all_features_list:
        all_features = np.vstack(all_features_list)
        csv_file_path = get_dir('user_photos_features.csv')
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Image ID', 'Feature Code', 'Landmark Index', 'X', 'Y']) # no race or sex since
            writer.writerows(all_features)                                             # we are not asking for it.
        npy_file_path = get_dir('user_photos_features.npy')
        np.save(npy_file_path, all_features)

if __name__ == "__main__":
    main()
