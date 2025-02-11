import random
import csv

CURRENT_COUNTRY = 'CHE'

COUNTRY_LIST = ['us', 'ae', 'bl']

print(COUNTRY_LIST[2] )

with open('_static/global/country_codes.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)  # Create reader object
    next(reader)  # Skip the header
    COUNTRIES = {row[0]: row[1] for row in reader}  # Store column 1 as keys, column 2 as values

COUNTRY_LIST = list(COUNTRIES.keys())

x = list(range(len(COUNTRY_LIST) + 1))

print(x)

total_endowment = 12

print(range(total_endowment + 1))