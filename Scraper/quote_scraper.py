'''
This python app scrapes the Wall Street Journal website for the closing stock
quotes for all of the publically listed companies in the S&P 500. This data
is stored in a database.
'''
import re
import csv
import datetime
import requests
import time

# import urllib.request # Delete this one
from bs4 import BeautifulSoup
from peewee import *

from database_info import Stock, db_info

# @TODO how to append to a text file
# @TODO clean up variable names
# @TODO migrate to requests module

loop_delay = 0 # delay in seconds to deal with potential server errors

closingDate = datetime.datetime.now()
minmax = re.compile(r'(\S+)\s\-\s(\S+)')
symbolList = []
csvfile = 'Resources/SP500.csv'
sp500_csv = csv.reader(csvfile)
for row in sp500_csv:
    symbolList.append(row)

# Pulling in the database login info from another file to keep login credentials private
db = database_info.db_info()

# class Stock(Model):
#     '''required class to setting up the database table'''
#     timestamp = DateTimeField(default=datetime.datetime.now())
#     ticker = CharField(max_length=6)
#     closing_price = DecimalField(max_digits=9, decimal_places=2)
#     minimum_price = DecimalField(max_digits=9, decimal_places=2)
#     maximum_price = DecimalField(max_digits=9, decimal_places=2)
#     volume = IntegerField()

#     class Meta:
#         database = db


def initialize():
    '''Connect to the database and create the table if it doesn't exist'''
    db.connect()
    db.create_tables([Stock], safe=True)


def did_not_work():
    '''In the event the ticker did not scrape, return NAN and log it'''
    print('{} didnt work due to an Attribute Error'.format(symbol))
            did_not_work_List.append(symbol)
            return {'ticker':symbol,
                    'closing_price':None,
                    'minimum_price':None,
                    'maximum_price':None,
                    'volume':None}

def quote_scraper(symbol):
    '''Scrapes the following stock quote information for the day:
    -Closing Price
    -Minimum Price
    -Maximum Price
    -Volume Traded
    '''
    try:
        quote_page = 'http://quotes.wsj.com/'+str(symbol)
        print('Scraping quote infomation for: {}'.format(symbol))

        # Setting up the soup
        # page = urllib.request.urlopen(quote_page)
        page = requests.get(quote_page)
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

        return {'ticker':symbol,
                'closing_price':float(closingPrice),
                'minimum_price':float(minRange),
                'maximum_price':float(maxRange),
                'volume':int(volumeTraded)}

    except AttributeError:
        did_not_work()

    except HTTPError:
        did_not_work()


def loop_scraper(list):
    '''Function that builds and returns the scraped data table'''
    scraped_stock_dict = []
    ticker_did_not_work_List = []

    for symbols in list:
        scraped_stock_dict.append(quote_scraper(symbols))

    time.sleep(loop_delay)
    return scraped_stock_dict, ticker_did_not_work_List


def write_to_DB(data_dict_list):
    '''Writing the entries in the database'''
    for row in data_dict_list:
         # Printing the results to monitor scraping results
        details = 'Price: {} | Price Range: {} - {} | Volume traded: {}'.format(
            row.closingPrice, row.minRange, row.maxRange, row.volumeTraded)
        print(details)

        Stock.create(timestamp=closingDate,
                        ticker=row.ticker,
                        closing_price=row.closing_price,
                        minimum_price=row.minimum_price,
                        maximum_price=row.maximum_price,
                        volume=row.volume)

        print('DONE \n')
        print('-'*len(details))


def write_to_log(time_to_finish, did_not_work_List):
    '''Output errors and time elapsed to the log'''
    output = '''
    ---------------------------------------------------
    Log Date: {}
    The following stock tickers had an Attribute Error:
    {}
    The program took this long to finish: {}
    ---------------------------------------------------
    '''.format(closingDate, did_not_work_List, time_elapsed)
    
    print(output)
    file = open('Resources/log.txt','w')
    file.write(output)
    file.close() 
    # file.append()

# start the database connection
initialize()

# Calculating the time it takes to complete all the database entries
start_time = datetime.datetime.now()

scraped_stock_dict, did_not_work_List = loop_scraper(symbolList)

end_time = datetime.datetime.now()
time_elapsed = end_time - start_time


