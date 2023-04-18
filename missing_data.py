import pandas as pd

# Load the dataset
paygap = pd.read_csv("data/pay_gap_Europe.csv")

##### ----- DATA CLEANING - MISSING VALUES ----- #####

# Total null value for each column
# print(paygap.isna().sum())

# Group by country and calculate the mean for all columns for each country
country_means = paygap.groupby('Country').mean()

# Iterate over the rows
for index, row in paygap.iterrows():
    # For the column in the df
    for column in paygap.columns:
        # Check if it is null and replace by mean
        if pd.isnull(row[column]):
            country_mean = country_means.loc[row['Country'], column]
            paygap.at[index, column] = country_mean

# Check if any rows that have at least one missing value
# print(paygap.isnull().any())

# Export df to csv
paygap.to_csv(r'data/data.csv')