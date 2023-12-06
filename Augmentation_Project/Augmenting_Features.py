import cv2
import numpy as np
import os


def load_feature_landmarks(facial_features, image_id, feature_to_int, feature_name):
    feature_landmarks = facial_features[
        (facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_to_int[feature_name])]
    return feature_landmarks[:, 3:5]


def resize_nose(img, facial_features, image_id, feature_to_int, scale_factor):
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')
    return resize_and_overlay_feature(img, nose_landmarks, scale_factor, width_margin_factor=0.2,
                                      height_margin_factor=0.1)


def resize_eyes(img, facial_features, image_id, feature_to_int, scale_factor):
    eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
    # Increased padding for eyes to capture eyelashes and surrounding area
    return resize_and_overlay_feature(img, eye_landmarks, scale_factor, width_margin_factor=0.25,
                                      height_margin_factor=0.4)


def resize_and_overlay_feature(img, feature_points, scale_factor, width_margin_factor, height_margin_factor):
    x_min, y_min = np.min(feature_points, axis=0).astype(int)
    x_max, y_max = np.max(feature_points, axis=0).astype(int)
    width_margin = int((x_max - x_min) * width_margin_factor)
    height_margin = int((y_max - y_min) * height_margin_factor)
    x_min = max(x_min - width_margin, 0)
    y_min = max(y_min - height_margin, 0)
    x_max = min(x_max + width_margin, img.shape[1])
    y_max = min(y_max + height_margin, img.shape[0])
    feature_region = img[y_min:y_max, x_min:x_max]
    feature_width = x_max - x_min
    feature_height = y_max - y_min
    scaled_width = int(feature_width * scale_factor)
    scaled_height = int(feature_height * scale_factor)
    scaled_feature = cv2.resize(feature_region, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)
    overlay_start_x = x_min + (feature_width - scaled_width) // 2
    overlay_start_y = y_min + (feature_height - scaled_height) // 2
    img[overlay_start_y:overlay_start_y + scaled_height,
    overlay_start_x:overlay_start_x + scaled_width] = scaled_feature
    return img


def main():
    facial_features = np.load('Augmentation_Project/facial_features.npy')
    feature_to_int = {'jawline': 0, 'eyebrows': 1, 'nose': 2, 'eyes': 3, 'lips': 4}
    image_directory = 'Augmentation_Project/original_images'
    augmented_directory = 'Augmentation_Project/augmented_images'
    nose_scale_factor = 1.25
    eye_scale_factor = 0.80

    if not os.path.exists(augmented_directory):
        os.makedirs(augmented_directory)

    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for img_path in image_paths:
        img = cv2.imread(img_path)
        image_id = image_paths.index(img_path)
        img = resize_nose(img, facial_features, image_id, feature_to_int, nose_scale_factor)
        img = resize_eyes(img, facial_features, image_id, feature_to_int, eye_scale_factor)

        augmented_img_name = f"augmented_{os.path.basename(img_path)}"
        augmented_img_path = os.path.join(augmented_directory, augmented_img_name)
        cv2.imwrite(augmented_img_path, img)


if __name__ == "__main__":
    main()

