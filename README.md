# Info

    usage: getYfinance.py [-h] [--version] [-t] [-r N] [-x | -j]
                          (-i | -b | -c | -s)
                          symbol [symbol ...]
    
    General purpose Yahoo! Finance scraper
    
    positional arguments:
      symbol                  ticker symbol(s)
    
    optional arguments:
      -h, --help              show this help message and exit
      --version               show program's version number and exit
      -t, --transpose         transpose rows and columns
      -r N, --record N        specify record N to print
      -x, --excel             print to excel instead of STDOUT
      -j, --json              print JSON to STDOUT
      -i, --income-statement  parse income statement
      -b, --balance-sheet     parse balance sheet
      -c, --cash-flow         parse cash flow
      -s, --summary           parse summary
    

## Acknowledgments

* most of the original code and concepts came from https://www.mattbutton.com/2019/01/24/how-to-scrape-yahoo-finance-and-extract-fundamental-stock-market-data-using-python-lxml-and-pandas/. It was a great headstart into what i was trying to do and there have been so many other great Internet resources.

