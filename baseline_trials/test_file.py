import random
import csv

CURRENT_COUNTRY = 'CHE'

COUNTRY_LIST = ['us', 'ae', 'bl']

print(COUNTRY_LIST[2] )



with open('_static/global/country_codes.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)  # Create reader object
    next(reader)  # Skip the header
    data = {row[0]: row[1] for row in reader}  # Store column 1 as keys, column 2 as values

# Extract columns as lists
COUNTRY_LIST = list(data.values())  # Second column

print(COUNTRY_LIST)

CURRENT_COUNTRYNAME = data.get("CHE")

print(CURRENT_COUNTRYNAME)