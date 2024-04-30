# Name: Rhiannon Barber
# This file does the statistical analysis based on the CarVer dataset.
# It finds averages globally, by race, by sex, and a combination.
# Each demographic's deviation is calculated from the global average.
# This is to be used in augmentation, to help minimize bias.

import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from pathlib import Path

def get_dir(relative_path):
    base_dir = Path(__file__).resolve().parent
    return base_dir.joinpath(relative_path).resolve()

def load_data(filepath):
    return np.load(filepath, allow_pickle=True)

def compute_distances(points): # finds the euclidean distance
    if len(points) < 2:
        return np.array([])
    distances = []
    for i in range(len(points) - 1):
        point1 = points[i]
        point2 = points[i + 1]
        distances.append(euclidean(point1, point2))
    return np.array(distances)

def compute_feature_averages(data):
    feature_points = {}
    feature_averages = {}
    for row in data:
        feature = int(row[2])  # finds the feature code from the array,
        if feature not in feature_points:
            feature_points[feature] = []
        feature_points[feature].append([float(row[4]), float(row[5])])  # gets the X Y
    for feature, points in feature_points.items():
        distances = compute_distances(np.array(points))  # finds the Euclidean distance.
        if distances.size > 0:
            mean_distance = np.mean(distances)  # finds the average of the distances.
            std_distance = np.std(distances)
            feature_averages[feature] = (mean_distance, std_distance) # uses a tuple to store the std dev and avg dist
        else:
            feature_averages[feature] = (0, 0)  # if nothing found, both are 0
    return feature_averages


def compute_std_dev(data, global_feature_averages):
    feature_points = {}
    feature_averages = {}
    for row in data:
        feature = int(row[2])  # get feature identifier
        if feature not in feature_points:
            feature_points[feature] = []
        feature_points[feature].append([float(row[4]), float(row[5])]) # get X Y

    for feature, points in feature_points.items():
        distances = compute_distances(np.array(points)) # find euclidean distance
        if distances.size > 0:
            global_mean = global_feature_averages[feature][0] # gets global average
            deviations = [d - global_mean for d in distances] # finds dev
            std_dev = np.std(deviations) # finds std deviation
            feature_averages[feature] = (global_mean, std_dev)
        else:
            feature_averages[feature] = (global_feature_averages[feature][0], 0)
    return feature_averages

def save_averages_npy(averages, filename):
    np.save(filename, averages)

def save_averages_csv(averages, filename):
    rows = []
    for feature, (mean, std) in averages.items():
        rows.append({'Feature': feature, 'AverageDistance': mean, 'StdDeviation': std})
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)

data = load_data('carver_features.npy')
global_feature_averages = compute_feature_averages(data)

race_sex_feature_averages = {}
race_averages = {}
for key, group in pd.DataFrame(data).groupby([6, 7]): # group by race and sex
    grouped_data = group.values
    averages = compute_std_dev(grouped_data, global_feature_averages)  #find the std dev
    race_sex_feature_averages[f"{key[0]}_{key[1]}"] = averages #save in dic where key = race and sex, value = avg

for key, group in pd.DataFrame(data).groupby([6]): # group by race
    grouped_data = group.values
    averages = compute_std_dev(grouped_data, global_feature_averages) #find the std dev
    race_averages[key[0]] = averages #save in dic where key = race, value = avg

# save to corresponding files.
save_averages_npy(global_feature_averages, 'global_feature_averages.npy')
save_averages_csv(global_feature_averages, 'global_feature_averages.csv')
for race_sex, averages in race_sex_feature_averages.items():
    npy_filename = f'{race_sex}_feature_averages.npy'
    csv_filename = f'{race_sex}_feature_averages.csv'
    save_averages_npy(averages, npy_filename)
    save_averages_csv(averages, csv_filename)
for race, averages in race_averages.items():
    npy_filename = f'{race}_feature_averages.npy'
    csv_filename = f'{race}_feature_averages.csv'
    save_averages_npy(averages, npy_filename)
    save_averages_csv(averages, csv_filename)
