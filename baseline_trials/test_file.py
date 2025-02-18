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

treatment_order = ['3PC give', '3PC comp', '3PP give', '3PP punish', '2PP give', '2PP punish']


index = next(i for i, v in enumerate(treatment_order) if "2PP" in v or "3PP" in v) # Find the smallest index of an element containing "2PP" or "3PP"

print(index)  # Output: 0