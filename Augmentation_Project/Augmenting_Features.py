import cv2
import numpy as np
import os

'''
Name: Rhiannon Barber
Date: January 25, 2024

This file contains the code for augmenting the facial features (nose, and eyes currently as of 1/25).

The augmentation is done to a hardcoded scale value, that needs to be changed to work with the std
deviation found in the Facial_Landmarking_Math.py file. 

As of 1/25 I have successfully blurred in the nose region for both larger and smaller scale values. 

Currently working on the eyes, though the code is not included in this file since it is very messy and not 
working correctly.  

In line comments have more detail on how certain things are working. 
'''


# This function constructs a file path for the specific directory.
def get_dir(filename):
    if "Augmentation_Project" in os.getcwd():
        filename = os.path.join(os.getcwd(), filename)
    else:
        filename = os.path.join(os.getcwd(), ("Augmentation_Project/" + filename))
    return filename


'''
This function loads the land markings found from the .npy file
returns the x,y coordinates from the data with are col 4 & 5.
'''


def load_feature_landmarks(facial_features, image_id, feature_to_int, feature_name):
    feature_landmarks = facial_features[
        (facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_to_int[feature_name])]
    return feature_landmarks[:, 3:5]


'''
 This function is responsible for resizing the nose.
 Gets the coordinates from the .npy file, and finds the feature named 'nose'
 returns the resized nose, with a margin factor to capture the nostrils
 region is overlaid on the image.
'''


def resize_nose(img, facial_features, image_id, feature_to_int, scale_factor):
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')
    return resize_and_overlay_feature(img, nose_landmarks, scale_factor, width_margin_factor=0.6,
                                      height_margin_factor=0.7)


'''
Similar to resize nose, but for eyes.
returns the resized eyes, with margin to capture eye lashes.
region is overlaid on the image.
'''


def resize_eyes(img, facial_features, image_id, feature_to_int, scale_factor):
    eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
    return resize_and_overlay_feature(img, eye_landmarks, scale_factor, width_margin_factor=0.25,
                                      height_margin_factor=0.4)


'''
This function is what is returned in the resize method. 
It's responsible for resizing the feature points, based on the scale factor, and the margin points. 
it is then overlaid onto the original image, and the 
'''


def resize_and_overlay_feature(img, feature_points, scale_factor, width_margin_factor, height_margin_factor):
    # Calculates the bounding box for the region, based on margin and landmarks.
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

    # cv2.resize takes the image, the scale to resize, and the interpolation: I chose linear since it was the
    # simplest approach to scaling the region with good results.
    scaled_feature = cv2.resize(feature_region, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)

    # Calculates the overlay starting horizontal margin for where the resized feature should be placed.
    # Discarding the fractional part to ensure whole integers for coordinates.
    overlay_start_x = x_min + (feature_width - scaled_width) // 2

    # Calculates the overlay starting vertical margin for where the resized feature should be placed.
    # Discarding the fractional part to ensure whole integers for coordinates.
    overlay_start_y = y_min + (feature_height - scaled_height) // 2
    img[overlay_start_y:overlay_start_y + scaled_height,
    overlay_start_x:overlay_start_x + scaled_width] = scaled_feature
    return img


'''
This function creates a mask where the area around the nose is white (255), to indicate the ROI. 
The rest of the mask is black, it can then be used in the blending.
The mask uses the land mark points, and margin to define the region of the mask. 
'''


def create_nose_mask(img, feature_points, width_margin_factor, height_margin_factor):
    mask = np.zeros_like(img)
    x_min, y_min = np.min(feature_points, axis=0).astype(int)
    x_max, y_max = np.max(feature_points, axis=0).astype(int)
    width_margin = int((x_max - x_min) * width_margin_factor)
    height_margin = int((y_max - y_min) * height_margin_factor)
    x_min = max(x_min - width_margin, 0)
    y_min = max(y_min - height_margin, 0)
    x_max = min(x_max + width_margin, img.shape[1])
    y_max = min(y_max + height_margin, img.shape[0])
    mask[y_min:y_max, x_min:x_max] = 255
    return mask


'''
Main loads the data from the .npy file, and makes an int value for the features. 
The directories for the original image, and augmented image are prepared to get image/place new image. 
Applies the resizing, and adds it to the original image. 
The images are then saved to the corresponding directory. 

'''


def main():
    facial_features = np.load(get_dir('facial_features.npy'))
    feature_to_int = {'jawline': 0, 'eyebrows': 1, 'nose': 2, 'eyes': 3, 'lips': 4}
    image_directory = get_dir('original_images')
    augmented_directory = get_dir('augmented_images')
    nose_scale_factor = 1.25
    eye_scale_factor = 0.80

    if not os.path.exists(augmented_directory):
        os.makedirs(augmented_directory)

    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for img_path in image_paths:
        img = cv2.imread(img_path)
        image_id = image_paths.index(img_path)
        original_img = img.copy()
        img = resize_nose(img, facial_features, image_id, feature_to_int, nose_scale_factor)
        nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')

        # the margins here for the mask affect where the bounds of the box are.
        nose_mask = create_nose_mask(original_img, nose_landmarks, width_margin_factor=0.4, height_margin_factor=0.1)

        # blurs the nose region, the kernel size changes the blur amount
        # ksize (0,0)  -> (width, height)
        # sigmaX -> 21 -> is the standard deviation of the kernel.
        # higher sigmaX = more blur. 21 showed good results. 24+ had some loss of detail.
        nose_mask_blurred = cv2.GaussianBlur(nose_mask, (0, 0), 21)

        # (nose_mask_blurred / 255) -> normalizes values to be between 0 & 1
        # areas are either 255 (white) rep by 1 or 0 (black) rep by 0
        # img * (nose_mask_blurred / 255) -> White areas are kept the same, and black areas are blurred.
        # original_img * (1 - (nose_mask_blurred / 255) -> Does above but in inverse.
        # white is now rep by 0, black is rep by 1
        # areas that are 0 (black) are now kept, and areas that are white are blurred.
        # adding them together gives the seamless blend of the images; so the nose is augmented and now blended in.
        img = img * (nose_mask_blurred / 255) + original_img * (1 - (nose_mask_blurred / 255))

        img = resize_eyes(img, facial_features, image_id, feature_to_int, eye_scale_factor)

        # saves the image with augmented_filename.jpeg for our way of telling the images apart, and ease of use in UI.
        # saved to the augmented_images dir.
        augmented_img_name = f"augmented_{os.path.basename(img_path)}"
        augmented_img_path = os.path.join(augmented_directory, augmented_img_name)
        cv2.imwrite(augmented_img_path, img)


if __name__ == "__main__":
    main()
