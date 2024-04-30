# Author: Rhiannon Barber
# This file does statistical analysis on a user uploaded photo.
# This is to be used after landmarking.
# Finds the average sizes of the user uploaded image, compares it to the demographics
# and finds which one it is closest to. Once it is found, the deviation is calculated from
# that demographic stored as ' Scale deviation ' which is what will be used to scale
# the augmentation for the features.

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial.distance import euclidean


def load_data(csv_path):
    return pd.read_csv(csv_path)

def calculate_feature_stats(data, global_averages):
    feature_data = {}
    for feature_code in data['Feature Code'].unique():  # iterating through each unique int for features
        feature_points = data[data['Feature Code'] == feature_code][['X', 'Y']]  # looking specifically at X and Y
        if len(feature_points) > 1:
            distances = []
            deviations = []
            for i in range(len(feature_points) - 1):  # from 1st point to second from last (avoid double count)
                # using int location to find the points.
                point1 = feature_points.iloc[i]
                point2 = feature_points.iloc[i + 1]
                distance = euclidean(point1, point2)  # get the euclidean distance.
                distances.append(distance)
                if feature_code in global_averages:
                    deviation = distance - global_averages[feature_code]  # find how dev from global.
                    deviations.append(deviation)
            average_distance = np.mean(distances)  # avg distance for each feature size.
            std_deviation = np.std(deviations) if deviations else 0
            feature_data[feature_code] = (average_distance, std_deviation)
        else:
            feature_data[feature_code] = (0, 0)  # if no points, set dev to 0
    return feature_data

def save_features(features, npy_path, csv_path):
    np.save(npy_path, features)
    data_items = [(code, stats[0], stats[1], stats[2] if len(stats) > 2 else None) for code, stats in features.items()]
    df = pd.DataFrame(data_items, columns=['Feature Code', 'Average Distance', 'Standard Deviation', 'Scale Deviation'])
    df.to_csv(csv_path, index=False)

def load_global_averages(npy_path):
    return np.load(npy_path, allow_pickle=True).item()


def load_demographic_data(directory_path):
    demographic_data = {}
    for npy_file in Path(directory_path).glob('*_feature_averages.npy'): # finds all the files to compare to
        demographic_name = npy_file.stem.split('_feature_averages')[0] # extracts the demo name
        demographic_data[demographic_name] = np.load(npy_file, allow_pickle=True).item()
    return demographic_data


def compare_user_to_demographics(user_feature_stats, demographic_data): # Iterates through the demos to find
    demographic_similarity = {}                                         # how the user compares.
    for demo_name, demo_stats in demographic_data.items():
        total_deviation = 0
        for feature_code, (user_avg, user_std) in user_feature_stats.items():
            if feature_code in demo_stats:
                _, demo_std = demo_stats[feature_code]
                total_deviation += (user_std - demo_std) ** 2
        demographic_similarity[demo_name] = np.sqrt(total_deviation)
    return demographic_similarity  # returns the similarities to find the min later.


def calculate_scale_deviation(user_feature_stats, demo_feature_stats):
    scale_deviations = {}
    paired_features = [(1, 2), (3, 4)] # this is so eyebrows and eyes get the same scale factor.

    for feature_code, (_, user_std) in user_feature_stats.items():
        if feature_code in demo_feature_stats:
            _, demo_std = demo_feature_stats[feature_code]
            scale_deviation = abs(user_std - demo_std)
            scale_deviations[feature_code] = round(scale_deviation, 1) # rounding to nearest 10th to use
                                                                       # each tenth as a % for scale factor

    for pair in paired_features:  # keeping the pairs together to keep same scale factor
        if all(p in scale_deviations for p in pair):
            avg_deviation = np.mean([scale_deviations[p] for p in pair])
            rounded_avg = round(avg_deviation, 1)
            for p in pair:
                scale_deviations[p] = rounded_avg

    return scale_deviations

def main():
    base_directory = Path(__file__).resolve().parent
    csv_path = base_directory / 'user_photos_features.csv'
    npy_path = base_directory / 'user_features.npy'
    csv_out_path = base_directory / 'user_features.csv'
    demographic_directory = '../CarVer_Statistics'

    global_averages = load_global_averages('../CarVer_Statistics/global_feature_averages.npy')
    demographic_data = load_demographic_data(demographic_directory)
    features_data = load_data(csv_path)
    user_feature_stats = calculate_feature_stats(features_data, global_averages)

    demographic_similarity = compare_user_to_demographics(user_feature_stats, demographic_data)
    closest_demographic = min(demographic_similarity, key=demographic_similarity.get)
    closest_demo_feature_stats = demographic_data[closest_demographic]
    scale_deviations = calculate_scale_deviation(user_feature_stats, closest_demo_feature_stats)

    for feature_code, stats in user_feature_stats.items():
        user_feature_stats[feature_code] = (stats[0], stats[1], scale_deviations.get(feature_code))

    save_features(user_feature_stats, npy_path, csv_out_path)

if __name__ == "__main__":  # will be removed once working in the system as a module. was running for testing.
    main()
