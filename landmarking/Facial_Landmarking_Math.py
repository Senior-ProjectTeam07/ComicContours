import numpy as np
from utils import get_dir

def calc_dist(pt1, pt2):
    return np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

def avg_feature_sizes(features, img_id):
    avg_sizes = {}
    for region, points in get_region_pts(features, img_id).items():
        dists = [calc_dist(points[i][3:], points[i + 1][3:]) for i in range(len(points) - 1)]
        avg_sizes[region] = np.mean(dists) if dists else 0
    return avg_sizes

def get_region_pts(features, img_id):
    regions = {
        'jawline': range(17),
        'eyebrows': range(17, 27),
        'nose': range(27, 36),
        'eyes': range(36, 48),
        'lips': range(48, 68)
    }
    img_features = features[features[:, 0] == img_id]
    return {region: img_features[np.isin(img_features[:, 2], indices)] for region, indices in regions.items()}

def global_avg_sizes(features):
    total_sizes = {region: [] for region in get_region_pts(features, 0).keys()}
    for img_id in np.unique(features[:, 0]):
        img_sizes = avg_feature_sizes(features, img_id)
        for region, size in img_sizes.items():
            total_sizes[region].append(size)
    return {region: np.mean(sizes) for region, sizes in total_sizes.items()}

def std_dev_features(features, global_avgs):
    deviations = {region: [] for region in global_avgs.keys()}
    for img_id in np.unique(features[:, 0]):
        img_sizes = avg_feature_sizes(features, img_id)
        for region, global_avg in global_avgs.items():
            dev = img_sizes[region] - global_avg
            deviations[region].append(dev)
    return {region: np.std(devs) for region, devs in deviations.items()}

def print_sizes_and_devs(features):
    global_avgs = global_avg_sizes(features)
    std_devs = std_dev_features(features, global_avgs)

    for img_id in np.unique(features[:, 0]):
        img_feature_sizes = avg_feature_sizes(features, img_id)
        print(f"Image ID {img_id}:")
        for region, size in img_feature_sizes.items():
            print(f"    Average size for {region}: {size}")
            print(f"    Standard deviation for {region}: {std_devs[region]}")

features = np.load(get_dir("data/facial_features.npy"))
print_sizes_and_devs(features)

