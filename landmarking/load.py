# load.py

'''
This function loads the land markings found from the .npy file
returns the x,y coordinates from the data with are col 4 & 5.
'''
def load_feature_landmarks(facial_features, image_id, feature_to_int, feature_name):
    feature_landmarks = facial_features[
        (facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_to_int[feature_name])]
    return feature_landmarks[:, 3:5]
