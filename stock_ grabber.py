import re
import datetime
import time

import urllib.request
from bs4 import BeautifulSoup
from peewee import *
import database_locator
import pandas as pd

# Establishing constant variables
minmax = re.compile(r'(\S+)\s\-\s(\S+)')
reader = pd.read_csv("SP500.csv", index_col=['Ticker symbol'])
symbolList = reader.index.tolist()
closingDate = datetime.datetime.now()
# Logging a list of stocks that did not get scraped
did_not_work_List = []

# Pulling in the database login info from another file to keep login credentials private
db = database_locator.db_info()

# Setting up the table
class Stock(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    ticker = CharField(max_length=6)
    closing_price = DecimalField(max_digits=9, decimal_places=2)
    minimum_price = DecimalField(max_digits=9, decimal_places=2)
    maximum_price = DecimalField(max_digits=9, decimal_places=2)
    volume = IntegerField()

    class Meta:
        database = db

# Connect to the database and create the table if it doesn't exist.
def initialize():
    db.connect()
    db.create_tables([Stock], safe=True)


# Function that grabs the stock quote information and saves to the database
def wsjQuoter(symbol):
    try:
        quote_page = 'http://quotes.wsj.com/'+str(symbol)
        print('Scraping quote infomation for: {}'.format(symbol))

        # Setting up the soup
        page = urllib.request.urlopen(quote_page)
        # page = requests.get(quote_page)
        soup = BeautifulSoup(page, "html.parser")

        # Scraping the closing price
        price_box = soup.find('span', id='quote_val')
        closingPrice = price_box.text.strip().replace(',', '')

        # After scraping, data_data list contains several data points
        # including max, min and volume traded
        data_data = []
        range_box = soup.findAll('span', attrs={'class': 'data_data'})
        for range in range_box:
            data_data.append(range.text.strip())

        # Scraping the max and min daily range values
        rangeSearch = re.search(minmax, data_data[3])
        minRange = rangeSearch.group(1).replace(',', '')
        maxRange = rangeSearch.group(2).replace(',', '')

        # Scraping the volume traded
        volumeTraded = data_data[1].replace(',', '')

        # Creating the entries in the database
        Stock.create(timestamp=closingDate,
                             ticker=symbol,
                             closing_price=float(closingPrice),
                             minimum_price=float(minRange),
                             maximum_price=float(maxRange),
                             volume=int(volumeTraded))

        # Printing the results to monitor scraping results
        details = 'Price: {} | Price Range: {} - {} | Volume traded: {}'.format(
            closingPrice, minRange, maxRange, volumeTraded)
        print(details)
        print('DONE \n')
        print('-'*len(details))

        time.sleep(1) # adding a small delay to deal with potential server errors

    except AttributeError:
        print('{} didnt work due to an Attribute Error'.format(symbol))
        did_not_work_List.append(symbol)
    except HTTPError:
        print('{} raised an HTTP Error'.format(symbol))
        did_not_work_List.append(symbol)


# Executing the magic
initialize()

# Calculating the time it takes to complete all the database entries
start = datetime.datetime.now()

for symbols in symbolList:
    wsjQuoter(symbols)

end = datetime.datetime.now()
time_elapsed = end - start

print('The following stock tickers had an Attribute Error:')
print(did_not_work_List)
print('The program took this long to finish:')
print(str(time_elapsed))

# @TODO this time calculation needs to be improved, its currently not working
