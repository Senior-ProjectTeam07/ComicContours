# augment.py

import cv2
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from augmentation.nose import resize_nose, create_nose_mask
from augmentation.eyes import create_eye_mask
from landmarking.load import load_feature_landmarks
from utils.file_utils import get_dir
from utils.img_utils import alpha_blend
from augmentation.make_image import make_eye_img, make_eye_img

def augment_nose(img_path, facial_features, image_id, feature_to_int, nose_scale_factor):
    img = cv2.imread(img_path)
    original_img = img.copy()
    img = resize_nose(img, facial_features, image_id, feature_to_int, nose_scale_factor)
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')
    nose_mask = create_nose_mask(original_img, nose_landmarks, width_margin_factor=0.4, height_margin_factor=0.1)
    nose_mask_blurred = cv2.GaussianBlur(nose_mask, (0, 0), 21)
    img = img * (nose_mask_blurred / 255) + original_img * (1 - (nose_mask_blurred / 255))
    return img

def augment_eyes(img, facial_features, image_id, feature_to_int):
    eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
    eyebrow_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyebrows')
    face_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'jawline')
    nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')

    # Split eye_landmarks and eyebrow_landmarks into two
    eye_landmarks1, eye_landmarks2 = np.array_split(eye_landmarks, 2)
    eyebrow_landmarks1, eyebrow_landmarks2 = np.array_split(eyebrow_landmarks, 2)

    # Delete outermost eyebrow landmark to make upper eye and eyebrow landmarks number the same
    eyebrow_landmarks1 = np.delete(eyebrow_landmarks1, 3, 0)
    eyebrow_landmarks2 = np.delete(eyebrow_landmarks2, 1, 0)

    # Delete bottom two eye landmarks
    eye_landmarks1 = np.delete(eye_landmarks1, [4, 5], 0)
    eye_landmarks2 = np.delete(eye_landmarks2, [4, 5], 0)

    # Expand eye_landmarks by half the distance from eyes to eyebrows
    result1 = (eye_landmarks1 - eyebrow_landmarks1) / 2
    result2 = (eye_landmarks2 - eyebrow_landmarks2) / 2

    # Insert bottom eye landmarks and expand downward
    result1 = np.append(result1, [[-(face_landmarks[0, 0] - eye_landmarks1[0, 0])/2, -result1[3, 1]/2]], axis=0)
    result1 = np.insert(result1, 4, [-result1[0, 0], -result1[3, 1]], axis=0)
    result2 = np.append(result2, [[result2[3, 0], -result2[3, 1]]], axis=0)
    result2 = np.insert(result2, 4, [-(face_landmarks[16, 0] - eye_landmarks2[3, 0])/2, -result2[3, 1]/2], axis=0)

    # Calculate expanded result into eye_landmarks
    eye_landmarks1, eye_landmarks2 = eye_landmarks1 - result1[:4],  eye_landmarks2 - result2[:4]

    # Create mask for eyes
    mask = create_eye_mask(eye_landmarks1, eye_landmarks2, img)

    # Create mask2 for eyes
    eye_landmarks1[0, 0] = eye_landmarks1[0, 0]+((face_landmarks[0, 0] - eye_landmarks1[0, 0])/2)  # make horizontal mask wider
    eye_landmarks2[3, 0] = eye_landmarks2[3, 0]+((face_landmarks[16, 0] - eye_landmarks2[3, 0])/2)  # make horizontal mask wider

    # Check if the 6th element exists before trying to access it
    if eye_landmarks1.shape[0] > 5:
        eye_landmarks1[5, 0] = eye_landmarks1[5, 0]-(face_landmarks[16, 0] - eye_landmarks2[3, 0])  # make horizontal mask wider

    if eye_landmarks2.shape[0] > 4:
        eye_landmarks2[4, 0] = eye_landmarks2[4, 0]+(face_landmarks[16, 0] - eye_landmarks2[3, 0])  # make horizontal mask wider

    mask2 = create_eye_mask(eye_landmarks1, eye_landmarks2, img)
    
    # Blur the mask to obtain natural result
    mask = cv2.GaussianBlur(mask, (99, 99), 32)
    mask2 = cv2.GaussianBlur(mask2, (99, 99), 32)

    # Put masks into image
    result = make_eye_img(img, mask2, face_landmarks, eyebrow_landmarks, img)
    result = make_eye_img(img, mask, face_landmarks, eyebrow_landmarks, img)
    return result

def augment_image():
    facial_features = np.load(get_dir('data/facial_features.npy'))
    feature_to_int = {'jawline': 0, 'eyebrows': 1, 'nose': 2, 'eyes': 3, 'lips': 4}
    image_directory = get_dir('data/original_images')
    augmented_directory = get_dir('data/augmented_images')
    nose_scale_factor = 1.25

    if not os.path.exists(augmented_directory):
        os.makedirs(augmented_directory)

    image_paths = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if
                   filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for img_path in image_paths:
        image_id = image_paths.index(img_path)
        img = augment_nose(img_path, facial_features, image_id, feature_to_int, nose_scale_factor)
        img = augment_eyes(img, facial_features, image_id, feature_to_int)
        augmented_img_name = f"augmented_{os.path.basename(img_path)}"
        augmented_img_path = os.path.join(augmented_directory, augmented_img_name)
        cv2.imwrite(augmented_img_path, img)

'''
def main():
    facial_features = np.load(get_dir('data/facial_features.npy'))
    feature_to_int = {'jawline': 0, 'eyebrows': 1, 'nose': 2, 'eyes': 3, 'lips': 4}
    image_directory = get_dir('data/original_images')
    augmented_directory = get_dir('data/augmented_images')
    nose_scale_factor = 1.25

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

        # saves the image with augmented_filename.jpeg for our way of telling the images apart, and ease of use in UI.
        # saved to the augmented_images dir.
        augmented_img_name = f"augmented_{os.path.basename(img_path)}"
        augmented_img_path = os.path.join(augmented_directory, augmented_img_name)
        cv2.imwrite(augmented_img_path, img)

        # START TO EYE AUGMENTATION #
        # Get landmarks for eyes and other facial features
        eye_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyes')
        eyebrow_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'eyebrows')
        face_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'jawline')
        nose_landmarks = load_feature_landmarks(facial_features, image_id, feature_to_int, 'nose')

        # Delete eye landmarks to make shape of numpy arrays the same
        left_eye, right_eye = np.array_split(eye_landmarks, 2)  # Delete the second outward landmark
        left_brow, right_brow = np.array_split(eyebrow_landmarks, 2)
        l_eye, r_eye = left_eye.copy(), right_eye.copy()

        # Delete outermost eyebrow landmark to
        # make upper eye and eyebrow landmarks number the same
        left_brow = np.delete(left_brow, 3, 0)
        right_brow = np.delete(right_brow, 1, 0)

        # Delete bottom two eye landmarks
        left_eye = np.delete(left_eye, 4, 0)
        left_eye = np.delete(left_eye, 4, 0)
        right_eye = np.delete(right_eye, 4, 0)
        right_eye = np.delete(right_eye, 4, 0)

        # Expand eye_landmarks by half the distance from eyes to eyebrows
        result1 = (left_eye - left_brow)
        result2 = (right_eye - right_brow)
        result1[0, 0] = -(face_landmarks[0, 0] - left_eye[0, 0])/2  # make horizontal mask wider
        result2[3, 0] = -((face_landmarks[16, 0] - right_eye[3, 0])/2)  # make horizontal mask wider
        result1[3, 0] = (left_eye[3, 0] - nose_landmarks[0, 0])/2   # Expand eye near nose horizontal
        result2[0, 0] = -(nose_landmarks[0, 0] - right_eye[0, 0])/2  # Expand eye near nose horizontal
        l_lower_expand = (result1[3, 1])  # Get the largest distance from results
        r_lower_expand = (result1[3, 1])   # Get the largest distance from results
        result1, result2 = result1 / 2, result2 / 2
        # Insert bottom eye landmarks and expand downward
        result1 = np.append(result1, [[-(face_landmarks[0, 0] - left_eye[0, 0])/2, -l_lower_expand/2]], axis=0)
        result1 = np.insert(result1, 4, [-result1[0, 0], -l_lower_expand], axis=0)
        result2 = np.append(result2, [[result2[3, 1], -r_lower_expand]], axis=0)
        result2 = np.insert(result2, 4, [-(face_landmarks[16, 0] - right_eye[3, 0])/2, -r_lower_expand/2], axis=0)
        # Calculate expanded result into eye_landmarks
        eye_landmarks1, eye_landmarks2 = l_eye - result1,  r_eye - result2

        # mask 1, makes mask for reduced eye
        mask = create_eye_mask(eye_landmarks1, eye_landmarks2, img)
        # mask 2, makes mask for blurred background of eye
        eye_landmarks1[0, 0] = eye_landmarks1[0, 0]+((face_landmarks[0, 0] - eye_landmarks1[0, 0])/2)  # make horizontal mask wider
        eye_landmarks2[3, 0] = eye_landmarks2[3, 0]+((face_landmarks[16, 0] - eye_landmarks2[3, 0])/2)  # make horizontal mask wider
        eye_landmarks1[5, 0] = eye_landmarks1[5, 0]-(face_landmarks[16, 0] - eye_landmarks2[3, 0])  # make horizontal mask wider
        eye_landmarks2[4, 0] = eye_landmarks2[4, 0]+(face_landmarks[16, 0] - eye_landmarks2[3, 0])  # make horizontal mask wider
        mask2 = create_eye_mask(eye_landmarks1, eye_landmarks2, img)

        # Blur the mask to obtain natural result
        blur = (3*int(result1[0, 0]))
        if not(blur % 2):
            blur = blur + 1
        mask = cv2.GaussianBlur(mask, (blur, blur), 99)
        mask2 = cv2.GaussianBlur(mask2, (99, 99), 32)

        # Put masks into image
        result = make_img(img, mask2, face_landmarks, eyebrow_landmarks, img, "mask2")
        result = make_img(img, mask, face_landmarks, eyebrow_landmarks, result, "mask")

        # Show result
        result = cv2.normalize(result, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        cv2.imwrite(augmented_img_path, result)

if __name__ == "__main__":
    main()'''