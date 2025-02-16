import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import show

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


df = load_ndjson_to_dataframe(file_path)

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


stats, df = compute_interarrival_statistics(df)
print(stats)
if df is not None:
    print(df.head(100))  # Display the first few rows
    plot_histogram(df, "interarrival_time")

    df.plot(x="timeStamp", y="interarrival_time", kind="scatter",
            title="Plot of 'timeStamp' against 'interarrival_time'", s=.1)
    plt.ylim(bottom=0)
plt.show()