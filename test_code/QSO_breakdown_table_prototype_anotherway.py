import pandas as pd
from tabulate import tabulate

def generate_combined_prototype():
    """
    Demonstrates the most robust solution: building the table with a
    pandas MultiIndex and then formatting it with the tabulate library.
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
    
    # 3. Create the DataFrame with a named index
    df = pd.DataFrame(data, index=[call1, call2], columns=columns)
    df.index.name = "--- 20M ---"

    # 4. Use tabulate to render the final table with psql format
    #    'keys' tells tabulate to use the DataFrame's index and columns.
    final_table = tabulate(
        df,
        headers='keys',
        tablefmt="psql",
        numalign="right"
    )

    print(final_table)


if __name__ == "__main__":
    generate_combined_prototype()