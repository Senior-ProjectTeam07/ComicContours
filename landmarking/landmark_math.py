# landmarking_math.py
import numpy as np
import sys
import os

# Ensure the current and parent directories are in the path for module imports
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from utils.file_utils import get_dir
from utils.landmark_utils import FACIAL_LANDMARKS_68_IDX, feature_to_int, int_to_feature

def calc_dist(pt1, pt2):
    """
    Calculate the Euclidean distance between two points, with strict type checking.
    """
    try:
        x1, y1 = float(pt1[0]), float(pt1[1])
        x2, y2 = float(pt2[0]), float(pt2[1])
        return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    except ValueError as e:
        raise ValueError("Both points must contain numerical values that are convertible to float.") from e

def avg_feature_sizes(features, img_id):
    """
    Calculate the average size of facial features for a given image.
    """
    avg_sizes = {}
    for region, points in get_region_pts(features, img_id).items():
        print(f"Calculating distances for region: {region} with points: {points}")  # Debug
        dists = []
        for i in range(len(points) - 1):
            dist = calc_dist(points[i][3:], points[i + 1][3:])
            dists.append(dist)
            print(f"Distance between {points[i][3:]} and {points[i + 1][3:]}: {dist}")  # Debug
        avg_sizes[region] = np.mean(dists) if dists else 0
        print(f"Average size for {region}: {avg_sizes[region]}")  # Debug
    return avg_sizes

def get_region_pts(features, img_id):
    """
    Get points for all facial feature regions for a specific image.
    """
    img_features = features[features[:, 0] == img_id]
    region_pts = {}
    for region, indices in FACIAL_LANDMARKS_68_IDX.items():
        region_features = img_features[np.isin(img_features[:, 1], range(*indices))]
        region_pts[region] = region_features
        # Debug: Output the number of points extracted for each region
        print(f"Region {region} points extracted: {len(region_features)}")
    return region_pts

def global_avg_sizes(features):
    """
    Calculate global average sizes of each facial feature across all images.
    """
    total_sizes = {region: [] for region in get_region_pts(features, 0).keys()}
    for img_id in np.unique(features[:, 0]):
        img_sizes = avg_feature_sizes(features, img_id)
        for region, size in img_sizes.items():
            total_sizes[region].append(size)
    return {region: np.mean(sizes) for region, sizes in total_sizes.items()}

def std_dev_features(features, global_avgs):
    """
    Calculate standard deviations of feature sizes from the global averages.
    """
    deviations = {region: [] for region in global_avgs.keys()}
    for img_id in np.unique(features[:, 0]):
        img_sizes = avg_feature_sizes(features, img_id)
        for region, global_avg in global_avgs.items():
            dev = img_sizes[region] - global_avg
            deviations[region].append(dev)
    return {region: np.std(devs) for region, devs in deviations.items()}

def print_sizes_and_devs(features):
    """
    Print the average sizes and standard deviations of facial features for each image.
    """
    global_avgs = global_avg_sizes(features)
    std_devs = std_dev_features(features, global_avgs)

    for img_id in np.unique(features[:, 0]):
        img_feature_sizes = avg_feature_sizes(features, img_id)
        print(f"Image ID {img_id}:")
        for region, size in img_feature_sizes.items():
            print(f"    Average size for {region}: {size:.2f}")
            print(f"    Standard deviation from global average for {region}: {std_devs[region]:.2f}")

features = np.load(get_dir("data/facial_features.npy"))
print_sizes_and_devs(features)