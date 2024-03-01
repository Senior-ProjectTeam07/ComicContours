# resize_overlay.py

import cv2
import numpy as np
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

'''
This function is what is returned in the resize method. 
It's responsible for resizing the feature points, based on the scale factor, and the margin points. 
it is then overlaid onto the original image, and the 
'''
def resize_and_overlay_feature(img, feature_points, scale_factor, width_margin_factor, height_margin_factor):
    # Check if the image is empty
    if img.size == 0:
        raise ValueError("Input image is empty.")

    # Check if feature points are empty
    if feature_points.size == 0:
        raise ValueError("Feature points are empty.")
    
    # Calculate the bounding box for the region, based on margin and landmarks.
    x_min, y_min = np.min(feature_points, axis=0).astype(int)
    x_max, y_max = np.max(feature_points, axis=0).astype(int)

    # Check if the bounding box is valid
    if x_min >= x_max or y_min >= y_max:
        raise ValueError("Feature region is empty or invalid due to incorrect bounding box.")

    width_margin = int((x_max - x_min) * width_margin_factor)
    height_margin = int((y_max - y_min) * height_margin_factor)
    x_min = max(x_min - width_margin, 0)
    y_min = max(y_min - height_margin, 0)
    x_max = min(x_max + width_margin, img.shape[1])
    y_max = min(y_max + height_margin, img.shape[0])

    # Ensure that the margins do not reduce the feature region to an invalid state
    if (x_max - x_min <= 0) or (y_max - y_min <= 0):
        raise ValueError("Feature region is invalid after applying margins.")

    # Ensure the feature region is not empty after applying margins
    feature_region = img[y_min:y_max, x_min:x_max]
    if feature_region.size == 0:
        raise ValueError("Feature region is empty after applying margins.")
    
    feature_width = x_max - x_min
    feature_height = y_max - y_min
    scaled_width = int(feature_width * scale_factor)
    scaled_height = int(feature_height * scale_factor)

    # Ensure the scaled dimensions are valid
    if scaled_width <= 0 or scaled_height <= 0:
        raise ValueError("Scaled feature dimensions are invalid.")
    
    # Takes the image, the scale to resize, and the interpolation:
    scaled_feature = cv2.resize(feature_region, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)

    # Calculate the overlay positions ensuring they are within bounds
    overlay_start_x = max(x_min + (feature_width - scaled_width) // 2, 0)
    overlay_end_x = min(overlay_start_x + scaled_width, img.shape[1])
    overlay_start_y = max(y_min + (feature_height - scaled_height) // 2, 0)
    overlay_end_y = min(overlay_start_y + scaled_height, img.shape[0])

    # Overlay the scaled feature onto the original image
    img[overlay_start_y:overlay_end_y, overlay_start_x:overlay_end_x] = scaled_feature

    return img