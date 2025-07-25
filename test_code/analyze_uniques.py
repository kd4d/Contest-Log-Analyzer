import pandas as pd
import sys

def analyze_uniques(file1, file2):
    """
    Analyzes two CSV files to find unique calls for each Mode/Band combination,
    considering only non-duplicate QSOs.

    Args:
        file1 (str): The file path for the first CSV file.
        file2 (str): The file path for the second CSV file.
    """
    try:
        # Load the full CSV files into pandas DataFrames
        df1_full = pd.read_csv(file1)
        df2_full = pd.read_csv(file2)
    except FileNotFoundError as e:
        print(f"Error: {e}. Please check the file paths.")
        return
    except Exception as e:
        print(f"An error occurred while reading the files: {e}")
        return

    # Get the labels for the files from the "MyCall" column of the original data
    label1 = df1_full['MyCall'].iloc[0]
    label2 = df2_full['MyCall'].iloc[0]

    # **MODIFICATION**: Filter DataFrames to include only non-duplicate QSOs
    # We use .copy() to prevent a SettingWithCopyWarning from pandas.
    df1 = df1_full[df1_full['Dupe'] == False].copy()
    df2 = df2_full[df2_full['Dupe'] == False].copy()

    print(f"Comparing {label1} and {label2}")
    print("Analysis based on non-duplicate QSOs only.\n")

    # Combine the "Mode" and "Band" columns to get all unique combinations
    modes_and_bands = pd.concat([df1[['Mode', 'Band']], df2[['Mode', 'Band']]]).drop_duplicates()

    # Iterate over each unique Mode/Band combination
    for index, row in modes_and_bands.iterrows():
        mode = row['Mode']
        band = row['Band']

        # Filter the (already dupe-filtered) DataFrames for the current Mode and Band
        df1_filtered = df1[(df1['Mode'] == mode) & (df1['Band'] == band)]
        df2_filtered = df2[(df2['Mode'] == mode) & (df2['Band'] == band)]

        # Get the set of calls from each filtered DataFrame
        calls1 = set(df1_filtered['Call'])
        calls2 = set(df2_filtered['Call'])

        # Find the calls that are unique to each file (symmetric difference)
        uniques1 = calls1 - calls2
        uniques2 = calls2 - calls1

        # If there are no unique calls for this combination, skip to the next
        if not uniques1 and not uniques2:
            continue

        print("-" * 50)
        print(f"Analysis for Mode: {mode}, Band: {band}")
        print("-" * 50)

        # Analyze and print the results for the first file
        if uniques1:
            print(f"\nUniques for {label1}: {len(uniques1)}")
            unique_df1 = df1_filtered[df1_filtered['Call'].isin(uniques1)]
            run_counts1 = unique_df1['Run'].value_counts().reindex(['Run', 'S&P', 'Unknown'], fill_value=0)
            for run_type, count in run_counts1.items():
                print(f"  {run_type}: {count}")

        # Analyze and print the results for the second file
        if uniques2:
            print(f"\nUniques for {label2}: {len(uniques2)}")
            unique_df2 = df2_filtered[df2_filtered['Call'].isin(uniques2)]
            run_counts2 = unique_df2['Run'].value_counts().reindex(['Run', 'S&P', 'Unknown'], fill_value=0)
            for run_type, count in run_counts2.items():
                print(f"  {run_type}: {count}")
        print("\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyze_logs.py <file1.csv> <file2.csv>")
    else:
        analyze_uniques(sys.argv[1], sys.argv[2])