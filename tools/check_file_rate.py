import pandas as pd
import json
import matplotlib.pyplot as plt

def load_ndjson_to_dataframe(file_path):
    try:
        # Open and read the file line by line
        with open(file_path, 'r') as file:
            data = [json.loads(line) for line in file]

        # Convert list of JSON objects into a pandas DataFrame
        df = pd.DataFrame(data)
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file '{file_path}': {e}")
        return None


# Example usage
file_path = "../results/1293/user_14_1965_time_series_1965.face_landmark.json"
df = load_ndjson_to_dataframe(file_path)

def compute_interarrival_statistics(df, timestamp_column="timeStamp"):
    try:
        if timestamp_column not in df.columns:
            raise ValueError(f"Column '{timestamp_column}' not found in the DataFrame.")

        # Sort the DataFrame by the timestamp column, if not already sorted
        df = df.sort_values(by=timestamp_column).reset_index(drop=True)

        # Compute interarrival times (differences between consecutive timestamps)
        df['interarrival_time'] = df[timestamp_column].diff()

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


stats, df = compute_interarrival_statistics(df)
print(stats)
if df is not None:
    print(df.head())  # Display the first few rows


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


plot_column_against_itself(df)
plt.show()