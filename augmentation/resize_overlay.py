# resize_overlay.py
import cv2
import numpy as np

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