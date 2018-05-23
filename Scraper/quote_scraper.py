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

from bs4 import BeautifulSoup
import peewee

from config import db

loop_delay = 0 # delay in seconds to deal with potential server errors
closing_date = datetime.datetime.now()
min_max = re.compile(r'(\S+)\s\-\s(\S+)')
symbol_list = []

with open('SP500.csv') as csvfile:
    sp500_csv = csv.DictReader(csvfile)
    for row in sp500_csv:
        symbol_list.append(row['Ticker symbol'])


class Stock_db(peewee.Model):
    '''required class to setting up the database table'''
    id = peewee.PrimaryKeyField(null=False)
    timestamp = peewee.DateTimeField(default=datetime.datetime.now())
    ticker = peewee.CharField(max_length=6)
    closing_price = peewee.DecimalField(max_digits=9, decimal_places=2)
    minimum_price = peewee.DecimalField(max_digits=9, decimal_places=2)
    maximum_price = peewee.DecimalField(max_digits=9, decimal_places=2)
    volume = peewee.IntegerField()

    class Meta:
        database = db


def initialize():
    '''Connect to the database and create the table if it doesn't exist'''
    db.connect()
    try:
        db.create_tables([Stock_db])
        print('Table created because it didnt exist!')
    except peewee.OperationalError:
        print('Table already exists!')


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


def write_to_DB(stock_info_dict):
    '''Write entries in the database'''
    progress_details = 'Saving stock info to database... \n'
    print(progress_details)

    stock_to_save = Stock_db(timestamp=closing_date,
                             ticker=stock_info_dict['ticker'],
                             closing_price=stock_info_dict['closing_price'],
                             minimum_price=stock_info_dict['minimum_price'],
                             maximum_price=stock_info_dict['maximum_price'],
                             volume=stock_info_dict['volume'])

    stock_to_save.save()

    print('DONE')
    print('-'*len(progress_details))


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
        page = requests.get(quote_page)
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

        stock_info = {'ticker': symbol,
                     'closing_price': float(closingPrice),
                     'minimum_price': float(minRange),
                     'maximum_price': float(maxRange),
                     'volume': int(volumeTraded)}

        details = 'Price: {} | Price Range: {} - {} | Volume traded: {}'
        print(details.format(closingPrice,
                             minRange,
                             maxRange,
                             volumeTraded))

        write_to_DB(stock_info)

    except AttributeError:
        did_not_work(symbol)


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
    file.write(output)
    file.close()


def loop_scraper(list):
    '''For loop that scrapes info on the stocks and saves them to the db'''

    for symbols in list:
        quote_scraper(symbols)
        time.sleep(loop_delay)

# start the database connection
initialize()

# Calculating the time it takes to complete all the database entries
start_time = datetime.datetime.now()

did_not_work_List = []

loop_scraper(symbol_list)

end_time = datetime.datetime.now()
time_elapsed = end_time - start_time

write_to_log(time_elapsed, did_not_work_List)

db.close()
