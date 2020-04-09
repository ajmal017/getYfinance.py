#!/usr/bin/env python

########################################
#
# Author:
#   David Klein
#
# Contact:
#    david@soinkleined.com 
# 
# Version:
#    0.2 - 2020-04-09 - David Klein <david@soinkleined.com>
#    	* added parse options and sort by date
#    	* added excel output
#    	* added help descriptions
#     0.1 - 2020-04-08 - David Klein <david@soinkleined.com>
#    	* initial release
# 
# References:
#    https://www.mattbutton.com/2019/01/24/how-to-scrape-yahoo-finance-and-extract-fundamental-stock-market-data-using-python-lxml-and-pandas/
#
########################################
version='0.2'
from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
import argparse 
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', None)
#pd.set_option('display.max_colwidth', None)
########################################
# ARGS
########################################
parser = argparse.ArgumentParser(description='General purpose Yahoo! Finance scraper')
parser.add_argument('--version', action='version', version='%(prog)s ' + version)
parser.add_argument('-d', '--by-date', action='store_true', help='print by date')
parser.add_argument('-x', '--excel', action='store_true', help='print to excel instead of STDOUT')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-i', '--income-statement', action='store_true', help='parse income statement')
group.add_argument('-b', '--balance-sheet', action='store_true', help='parse balance sheet')
group.add_argument('-c', '--cash-flow', action='store_true', help='parse cash flow')
args, remaining_argv = parser.parse_known_args()
symbol = remaining_argv[0]
symbol = symbol.upper()
########################################
#
########################################
if args.income_statement:
    url = "https://finance.yahoo.com/quote/%s/financials?p=%s"%(symbol,symbol)
    type = 'Income Statement'
elif args.balance_sheet:
    url = "https://finance.yahoo.com/quote/%s/balance-sheet?p=%s"%(symbol,symbol)
    type = 'Balance Sheet'
elif args.cash_flow:
    url = "https://finance.yahoo.com/quote/%s/cash-flow?p=%s"%(symbol,symbol)
    type = 'Cash Flow'

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

if not args.excel:
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

if args.excel:
    date = datetime.today().strftime('%Y-%m-%d')
    file = symbol + '-' + type.replace(' ','_') + '-' + date + '.xlsx'
    writer = pd.ExcelWriter(file)
if args.by_date:
    numeric_columns = list(df.columns)[1::] # Take all columns, except the first (which is the 'Date' column)
    # This breaks as 'Deferred revenues' is not a unique row
    for column_name in numeric_columns:
        df[column_name] = df[column_name].str.replace(',', '') # Remove the thousands separator
        df[column_name] = df[column_name].astype(np.float64) # Convert the column to
    if args.excel:
    	df.to_excel(writer,type)
    	print('Writing ' + file)
    	writer.save()
    else:
    	print(df)
else:
    df = df.transpose()
    if args.excel:
    	df.to_excel(writer,type)
    	print('Writing ' + file)
    	writer.save()
    else:
    	# Don't print column numbers
    	print(df.to_string(header=False))
