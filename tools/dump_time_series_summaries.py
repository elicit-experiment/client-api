import pandas as pd
import json
import matplotlib.pyplot as plt

# Load the CSV file with header
file_path = '../results/1295/user_11/datapoints.json'
with open(file_path, 'r') as file:
    summaries = json.load(file)

data_points = []

for summary in summaries:
    if summary['point_type'] == 'send_points_summary' and summary['kind'] == 'face_landmark':
        data_points.append({
            'datetime': summary['datetime'],
            'queued': summary['value']['queued'],
            'posted': summary['value']['posted'],
            'acknowledged': summary['value']['acknowledged'],
            'posted_bytes': summary['value']['posted_bytes'],
            'posted_compressed_bytes': summary['value']['posted_compressed_bytes'],
            'acknowledged_bytes': summary['value']['acknowledged_bytes'],
            'acknowledged_compressed_bytes': summary['value']['acknowledged_compressed_bytes'],
        })

data = pd.DataFrame(data_points)
data['datetime'] = data['datetime'] - data['datetime'].min()
data = data.sort_values(by='datetime')

print(data.size)

# Display the first few rows of the new dataframe
print(data.head(100))

print(data.columns)

# Chart the specified columns against 'datetime'
plt.figure(figsize=(10, 6))

# for column in ['posted_bytes', 'posted_compressed_bytes', 'acknowledged_bytes', 'acknowledged_compressed_bytes']:
#     if column in data.columns:
#         plt.scatter(data['datetime'], data[column], label=column)


columns_to_plot = ['queued', 'posted', 'acknowledged']
data = data[[col for col in columns_to_plot if col in data.columns] + ['datetime']]

print(data.head())
# Plot stacked bar chart
plt.figure(figsize=(10, 6))

# Stacked bar chart structure
bottom_stack = None
for column in columns_to_plot:
    if column in data.columns:
        if bottom_stack is None:
            plt.bar(data['datetime'], data[column], label=column)
            bottom_stack = data[column]
        else:
            plt.bar(data['datetime'], data[column], bottom=bottom_stack, label=column)
            bottom_stack += data[column]


plt.title('Data Trends Over Time')
plt.xlabel('Datetime')
plt.ylabel('count')
plt.legend()
plt.grid()
plt.show()
