'''
This python script scrapes the Wall Street Journal website for the closing
stock quotes for all of the publically listed companies in the S&P 500.
This data is stored in a database.

Then pulls the most recent couple days of stock performance from
a database and inserts the following into another MongoDB:
- daily change information for all S&P500 stocks
- daily change information by sector
'''
import re
from bs4 import BeautifulSoup
import csv
import datetime
import dns
import pandas as pd
import peewee
import requests
import time

from sqlalchemy import create_engine
from connstring import connstr, conn_string_mongo
from pymongo import MongoClient
from config import db

loop_delay = 0  # delay in seconds to deal with potential server errors
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


#################################
# Inserting the scraped data
#################################

sp500_df = pd.read_csv('SP500.csv', index_col='Ticker symbol')
wanted_cols = ['Security', 'GICS Sector', 'GICS Sub Industry']
sp500_df = sp500_df[wanted_cols]
sp500_df.columns = ['Company Name', 'Sector', 'Sub Industry']

engine = create_engine(connstr)


def pull_in_stock_data(query):
    with engine.connect() as conn, conn.begin():
        return pd.read_sql(query, conn)


cols = 'timestamp, ticker, closing_price, minimum_price, maximum_price, volume'
query = 'select {} from stock_db where timestamp in (select timestamp from stock_db) order by timestamp DESC, ticker ASC'.format(
    cols)
df = pull_in_stock_data(query)

most_recent_days = list(df['timestamp'].sort_values(ascending=False).unique())
today = most_recent_days[0]
yesterday = most_recent_days[1]


cols = ['ticker', 'timestamp']
pre_df = df[(df['timestamp'] == today) | (df['timestamp'] == yesterday)].copy()

df2 = pre_df['ticker'].value_counts().to_frame()
keep_list = list(df2[df2['ticker'] == 2].index)
keep_list

analysis_df = pre_df[pre_df['ticker'].isin(keep_list)]

analysis_df = pd.merge(analysis_df, sp500_df, how='inner',
                       left_on='ticker', right_index=True)

analysis_df.sort_values(cols, ascending=[True, False], inplace=True)
analysis_df.set_index(cols, inplace=True)

#################################
# Calculating the delta % into a dataframe
#################################

names = []
dates = []
delta_percent = []
quote_price = []
delta_amount = []
volume = []
sector = []
sub_industry = []


def get_percent_changes(lst):
    for companies in lst:
        names.append(analysis_df.loc[companies]['Company Name'][0])
        dates.append(analysis_df.loc[companies].index[0])

        company = analysis_df.loc[companies]
        today = company['closing_price'][0]
        yesterday = company['closing_price'][1]

        delta = (today - yesterday)
        delta_amount.append(delta)

        delta_pct = (delta / yesterday) * 100
        delta_percent.append(round(delta_pct, 2))

        quote_price.append(today)
        volume.append(company['volume'][0])
        sector.append(company['Sector'][0])
        sub_industry.append(company['Sub Industry'][0])


get_percent_changes(keep_list)

data = {'Company': names,
        'date': dates,
        'growth': delta_percent,
        'quote price': quote_price,
        'increase amount': delta_amount,
        'volume': volume,
        'Sector': sector,
        'Sub Industry': sub_industry}


df3 = pd.DataFrame(data, index=keep_list)

df3 = df3.sort_values('growth', ascending=False).reset_index().rename(
    columns={'index': "Ticker"})
date = df3['date'][0]
stock_df_for_insert = df3.reset_index()
stock_df_for_insert.rename(columns={'index': 'rank'})

#####################
# sectors
#####################


sector_df = analysis_df.reset_index().copy()
sector_df = sector_df.groupby(
    ['Sector', 'timestamp']).sum().sort_index(ascending=[True, False])

delta_percent = []


def get_percent_changes2(lst):
    for companies in lst:
        company_performance = sector_df.loc[companies]['closing_price']
        today = company_performance[0]
        yesterday = company_performance[1]

        delta = (today - yesterday)
        delta_pct = (delta / yesterday) * 100
        delta_percent.append(round(delta_pct, 2))


use_lst = list(sector_df.index.levels[0])
get_percent_changes2(use_lst)

data = {'pct_delta': delta_percent}


sector_df_for_insert = pd.DataFrame(data, index=use_lst).sort_values(
    'pct_delta', ascending=False).reset_index()
sector_df_for_insert.rename(columns={'index': 'Sector'}, inplace=True)
sector_df_for_insert = sector_df_for_insert.reset_index()
sector_df_for_insert.rename(columns={'index': 'Rank'}, inplace=True)

sector_data = sector_df_for_insert.to_dict('records')

##############################
# Inserts
##############################


client = MongoClient(conn_string_mongo)
db = client.test_database
stockData = db.stockData
sectorData = db.sectorData

sector_document = {"date": date,
                   "data": sector_data}

sectorData_id = sectorData.insert_one(sector_document).inserted_id
sectorData_id

stockData.insert_many(stock_df_for_insert.to_dict('records'))
print('Script Done')
