#!/usr/bin/env python

########################################
#
# Author: David Klein
#
# Contact: david@soinkleined.com 
# 
# Version: 0.1 - 2020-04-08 - David Klein <david@soinkleined.com>
#
# References:
#		https://www.mattbutton.com/2019/01/24/how-to-scrape-yahoo-finance-and-extract-fundamental-stock-market-data-using-python-lxml-and-pandas/
#
########################################
from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
import sys
import argparse 

########################################
# ARGS
########################################
parser = argparse.ArgumentParser(description='General purpose Yahoo! Finance scraper')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-i', '--income-statement', action='store_true')
group.add_argument('-b', '--balance-sheet', action='store_true')
group.add_argument('-c', '--cash-flow', action='store_true')
args, remaining_argv = parser.parse_known_args()
symbol = remaining_argv[0]
########################################
#
########################################
if args.income_statement:
    url = 'https://finance.yahoo.com/quote/' + symbol + '/financials?p=' + symbol
elif args.balance_sheet:
    url = 'https://finance.yahoo.com/quote/' + symbol + '/balance-sheet?p=' + symbol
elif args.cash_flow:
    url = 'https://finance.yahoo.com/quote/' + symbol + '/cash-flow?p=' + symbol

# Set up the request headers that we're going to use, to simulate
# a request by the Chrome browser. Simulating a request from a browser
# is generally good practice when building a scraper
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

# Fetch the page that we're going to parse, using the request headers
# defined above
page = requests.get(url, headers)

# Parse the page with LXML, so that we can start doing some XPATH queries
# to extract the data that we want
tree = html.fromstring(page.content)

# Smoke test that we fetched the page by fetching and displaying the H1 element
print(tree.xpath("//h1/text()"))

table_rows = tree.xpath("//div[contains(@class, 'D(tbr)')]")

# Ensure that some table rows are found; if none are found, then it's possible
# that Yahoo Finance has changed their page layout, or have detected
# that you're scraping the page.
assert len(table_rows) > 0

parsed_rows = []

for table_row in table_rows:
    parsed_row = []
    el = table_row.xpath("./div")
    
    none_count = 0
    
    for rs in el:
        try:
            (text,) = rs.xpath('.//span/text()[1]')
            parsed_row.append(text)
        except ValueError:
            parsed_row.append(np.NaN)
            none_count += 1

    if (none_count < 4):
        parsed_rows.append(parsed_row)

df = pd.DataFrame(parsed_rows)
df = df.set_index(0) # Set the index to the first column: 'Period Ending'.
df = df.transpose() # Transpose the DataFrame, so that our header contains the account names

# Rename the "Breakdown" column to "Date"
columns = list(df.columns)
columns[0] = 'Date'
df = df.set_axis(columns, axis='columns', inplace=False)
df = df.transpose() # Transpose the DataFrame, so that our header contains the account names

# Don't print column numbers
print(df.to_string(header=False))
