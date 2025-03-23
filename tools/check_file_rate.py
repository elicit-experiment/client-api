import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import show
import hashlib

# Set path from which to load the face landmarker json.
file_path = "../results/1298/user_10/1981_time_series_1981.face_landmark_uncompressed.json"

def load_ndjson_to_dataframe(file_path):
    try:
        # Open and read the file line by line
        with open(file_path, 'r') as file:
            data = [json.loads(line) for line in file]

        # Convert list of JSON objects into a pandas DataFrame
        df = pd.DataFrame(data)

        return df.sort_values(by="timeStamp").reset_index(drop=True)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file '{file_path}': {e}")
        return None


def compute_interarrival_statistics(df, timestamp_column="timeStamp"):
    try:
        if timestamp_column not in df.columns:
            raise ValueError(f"Column '{timestamp_column}' not found in the DataFrame.")

        # Sort the DataFrame by the timestamp column, if not already sorted
        df = df.sort_values(by=timestamp_column).reset_index(drop=True)

        # Compute interarrival times (differences between consecutive timestamps)
        df['interarrival_time'] = df[timestamp_column].diff()

        print(df.head(50))
        # Drop any NA values (first interarrival time will be NaN)
        interarrival_times = df['interarrival_time'].dropna()

        # Compute statistics
        stats = {
            'mean': interarrival_times.mean(),
            'median': interarrival_times.median(),
            'std': interarrival_times.std(),
            'min': interarrival_times.min(),
            'max': interarrival_times.max(),
            'total_count': len(interarrival_times)  # Count of valid interarrival times
        }

        return stats, df  # Returning the stats and DataFrame with interarrival times

    except ValueError as e:
        print(f"Error: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

# Plot the timeStamp column against itself
def plot_column_against_itself(df, column="timeStamp"):
    try:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in the DataFrame.")

        df['timeStamp'] = (df['timeStamp'] - df['timeStamp'].min())/1000.0

        # Plot the column against itself
        df.plot(x=column, y=column, kind="scatter", title=f"Plot of '{column}' against itself", s=.1)
        print(f"Plot for column '{column}' has been displayed.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while plotting: {e}")


def plot_histogram(df, column):
    """
    Function to plot a histogram for a specified column in a DataFrame.
    """
    try:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in the DataFrame.")

        # Drop any missing or NaN values
        non_na_values = df[column].dropna()

        # Plot the histogram
        plt.hist(non_na_values, bins=range(0, int(non_na_values.max()) + 2), alpha=0.7, color='blue')
        plt.title(f"Histogram of '{column}'")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.ylim(left=0)
        plt.grid(True)
        print(f"Histogram for column '{column}' has been displayed.")
        show()
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while plotting the histogram: {e}")


df = load_ndjson_to_dataframe(facelandmark_file_path)
stats, df = compute_interarrival_statistics(df)
print(stats)
if df is not None:
    print(df.head(100))  # Display the first few rows
    plot_histogram(df, "interarrival_time")

    df.plot(x="timeStamp", y="interarrival_time", kind="scatter",
            title="Plot of 'timeStamp' against 'interarrival_time'", s=.1)
    plt.ylim(bottom=0)
plt.show()


raw_file_name = facelandmark_file_path#.replace("_uncompressed", '')
hash_counts = {"face_landmarks_hash": {}, "blendshapes_hash": {}}

def compute_hash_bucket_counts(hash_dict):
    """
    Computes and returns counts for each hash bucket.
    """
    counts = {}
    for key, count in hash_dict.items():
        counts[count] = counts.get(count, 0) + 1
    return counts

def compute_values(filename, landmark_name = 'faceLandmarks', blendshape_name = 'blendshapes'):
    total_counts = 0
    with open(filename, 'r') as file:
        for line in file:
            if line.strip() == "":
                continue

            value = json.loads(line)
            total_counts += 1
            # Calculate hashes for face landmarks and blendshapes
            if len(value[landmark_name]) < 1:
                continue
            face_landmarks_hash = hashlib.md5(json.dumps(value[landmark_name][0]).encode('utf-8')).hexdigest()
            blendshapes_hash = hashlib.md5(json.dumps(value[blendshape_name][0]).encode('utf-8')).hexdigest()

            # Track and display counts of each hash
            hash_counts["face_landmarks_hash"][face_landmarks_hash] = hash_counts["face_landmarks_hash"].get(
                face_landmarks_hash, 0) + 1
            hash_counts["blendshapes_hash"][blendshapes_hash] = hash_counts["blendshapes_hash"].get(blendshapes_hash, 0) + 1

    # Compute and display the bucket counts
    face_landmarks_bucket_counts = compute_hash_bucket_counts(hash_counts["face_landmarks_hash"])
    blendshapes_bucket_counts = compute_hash_bucket_counts(hash_counts["blendshapes_hash"])

    print("Face Landmarks Hash Bucket Counts:", face_landmarks_bucket_counts)
    print("Blendshapes Hash Bucket Counts:", blendshapes_bucket_counts)

compute_values(raw_file_name, 'faceLandmarks', 'faceBlendshapes')