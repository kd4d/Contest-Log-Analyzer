import pandas as pd

def generate_dataframe_prototype():
    """
    Generates the desired table output using a pandas DataFrame with a
    MultiIndex header and the built-in to_string() method.
    """
    # 1. Define the multi-level header structure
    headers = [
        ('', 'Total'), ('', 'Unique'), ('', 'Common'),
        ('Unique QSOs', 'Run'), ('Unique QSOs', 'S&P'), ('Unique QSOs', 'Unk'),
        ('Common QSOs', 'Run'), ('Common QSOs', 'S&P'), ('Common QSOs', 'Unk')
    ]
    columns = pd.MultiIndex.from_tuples(headers)

    # 2. Hardcoded mock data
    call1 = "K1ABC"
    call2 = "W1XYZ"
    data = [
        [
            15230, 5110, 10120,
            4100, 900, 110,
            6000, 4000, 120
        ],
        [
            14500, 4380, 10120,
            3800, 500, 80,
            6100, 3900, 120
        ]
    ]
    
    # 3. Create the DataFrame
    df = pd.DataFrame(data, index=[call1, call2], columns=columns)

    # 4. Print the DataFrame using to_string()
    print("--- 20M ---")
    print(df.to_string())


if __name__ == "__main__":
    generate_dataframe_prototype()