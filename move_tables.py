from sqlalchemy import create_engine
import pandas as pd

# Define connection URLs for both databases
source_url = 'mysql://root:xEkkvZHDuwVxfhYziMKMxYytsmKvOfSB@junction.proxy.rlwy.net:27797/railway'
destination_url = 'mysql://root:xEkkvZHDuwVxfhYziMKMxYytsmKvOfSB@junction.proxy.rlwy.net:27797/Predictions'

# Create engines for source and destination
source_engine = create_engine(source_url)
destination_engine = create_engine(destination_url)

# Load the data from railway.results
query = "SELECT * FROM results"
results_df = pd.read_sql(query, con=source_engine)

# Write the data to Predictions.results
table_name = 'results'
results_df.to_sql(table_name, con=destination_engine, if_exists='replace', index=False)

# Close the connections
source_engine.dispose()
destination_engine.dispose()

print(f"Table {table_name} has been moved from Railway to Predictions.")
