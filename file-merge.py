import os
import pandas as pd

# Get the current working directory
directory = os.getcwd()

# Collect all CSV files that match the pattern
file_list = [f for f in os.listdir(directory) if f.startswith('data_') and f.endswith('.csv')]

# Sort files if needed (e.g., by numeric order in their names)
file_list.sort()

# Initialize an empty list to store DataFrames
dataframes = []

# Loop through and read each file
for file in file_list:
    file_path = os.path.join(directory, file)
    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Concatenate all DataFrames
merged_df = pd.concat(dataframes, ignore_index=True)

# Save the merged DataFrame to a new file
output_file = os.path.join(directory, 'merged_data.csv')
merged_df.to_csv(output_file, index=False)

print(f"Merged data saved to {output_file}")
