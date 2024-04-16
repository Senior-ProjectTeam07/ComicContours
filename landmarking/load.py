# load.py
def load_feature_landmarks(facial_features, image_id, feature_to_int, feature_name):
    
    # Check if the facial_features array is empty or not a 2D array
    if facial_features.size == 0 or len(facial_features.shape) != 2:
        raise ValueError("facial_features array is empty or not correctly formatted.")
    
    # Filter the landmarks for the specified image_id and feature
    mask = (facial_features[:, 0] == image_id) & (facial_features[:, 1] == feature_to_int.get(feature_name, -1))
    filtered_landmarks = facial_features[mask]
    
    # Check if there are any landmarks after filtering
    if filtered_landmarks.size == 0:
        raise ValueError(f"No landmarks found for image_id {image_id} and feature '{feature_name}'.")
    
    return filtered_landmarks[:, 3:5]