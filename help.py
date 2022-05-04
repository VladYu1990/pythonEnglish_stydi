import pandas as pd

# Get data - reading the CSV file
from pandas import mpu
df = mpu.pd.example_df()

# Convert
tuples = [[row[col] for col in df.columns] for row in df.to_dict('records')]
