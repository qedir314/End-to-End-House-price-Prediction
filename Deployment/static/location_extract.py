import pandas as pd
import json

# Read the CSV
df = pd.read_csv('..//..//Data/raw_data1.csv')

# Convert to JSON
locations_json = df[['Location1', 'Location2']].drop_duplicates().to_json(orient='records')

# Write to a file or pass to template
print(locations_json)