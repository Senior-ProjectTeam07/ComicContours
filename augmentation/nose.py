# nose.py
import numpy as np
from landmarking import load_feature_landmarks
from augmentation import resize_and_overlay_feature

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