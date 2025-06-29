import pandas as pd

def get_16_types():
    df = pd.read_csv("./csv/combined_mbti_df.csv")
    mbti_types = df["mbti"].drop_duplicates().to_list()
    return mbti_types

playlist_features = [
    "danceability",
    "energy",
    "mode",
    "speechiness",
    "liveness",
    "valence",
    "tempo",
    "instrumentalness",
]

keep_col = [
    'danceability_mean', 'energy_mean', 'mode_mean', 'speechiness_mean',
    'liveness_mean', 'valence_mean', 'tempo_mean', 'instrumentalness_mean'
]

# SHORTEN NAME, ADD IT WITH ...
MAX_LEN = 20
def shorten_name(name):
    if len(name) < MAX_LEN:
        return name

    name = name[:20] + '...' 
    return name
