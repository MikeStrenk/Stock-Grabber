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
# import PyMySQL.cursors
# https://pymysql.readthedocs.io/en/latest/user/examples.html

from config import Stock_db, db_info, loop_delay

# @TODO how to append to a text file
# @TODO clean up variable names
# @TODO missing a for loop to go through the symbolList

closing_date = datetime.datetime.now()
min_max = re.compile(r'(\S+)\s\-\s(\S+)')
symbol_list = []

with open('SP500.csv') as csvfile:
    sp500_csv = csv.DictReader(csvfile)
    for row in sp500_csv:
        symbol_list.append(row['Ticker symbol'])

# Pulling in the database login info from another file
db = db_info()


def initialize():
    '''Connect to the database and create the table if it doesn't exist'''
    db.connect()
    db.create_tables([Stock_db], safe=True)


def did_not_work(ticker_symbol):
    '''In the event the ticker did not scrape, return NAN and log it'''
    try:
        print('{} didnt work due to an Attribute Error'.format(ticker_symbol))
        did_not_work_List.append(ticker_symbol)
        return {'ticker': ticker_symbol,
                'closing_price': None,
                'minimum_price': None,
                'maximum_price': None,
                'volume': None}
    except AttributeError:
        pass


def loop_scraper(list):
    '''Function that builds and returns the scraped data table'''

    for symbols in list:
        scraped_stock_dict.append(quote_scraper(symbols))

    time.sleep(loop_delay)


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
        soup = BeautifulSoup(page.text, "html.parser")

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
        rangeSearch = re.search(min_max, data_data[3])
        minRange = rangeSearch.group(1).replace(',', '')
        maxRange = rangeSearch.group(2).replace(',', '')

        # Scraping the volume traded
        volumeTraded = data_data[1].replace(',', '')

        stockinfo = {'ticker': symbol,
                     'closing_price': float(closingPrice),
                     'minimum_price': float(minRange),
                     'maximum_price': float(maxRange),
                     'volume': int(volumeTraded)}

        scraped_stock_dict.append(stockinfo)

        print(stockinfo)

    except AttributeError:
        did_not_work(symbol)

    # except HTTPError:
    #     did_not_work()


def write_to_DB(data_dict_list):
    '''Writing the entries in the database'''
    for row in data_dict_list:
        # Printing the results to monitor scraping results
        details = 'Price: {} | Price Range: {} - {} | Volume traded: {}'
        details.format(row.closingPrice,
                       row.minRange,
                       row.maxRange,
                       row.volumeTraded)
        print(details)

        stock_to_save = Stock.create(timestamp=closingDate,
                                     ticker=row.ticker,
                                     closing_price=row.closing_price,
                                     minimum_price=row.minimum_price,
                                     maximum_price=row.maximum_price,
                                     volume=row.volume)

        stock_to_save.save()

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
    '''.format(closing_date, did_not_work_List, time_elapsed)

    print(output)
    file = open('log.txt', 'a')
    file.append(output)
    file.close()


# start the database connection
initialize()

# Calculating the time it takes to complete all the database entries
start_time = datetime.datetime.now()

scraped_stock_dict = []
did_not_work_List = []

loop_scraper(symbol_list)

end_time = datetime.datetime.now()
time_elapsed = end_time - start_time


print(scraped_stock_dict)

db.close()
