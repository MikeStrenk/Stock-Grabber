'''
This python script pulls the most recent couple days of stock performance from
a database and inserts the following into another MongoDB:
- daily change information for all S&P500 stocks
- daily change information by sector
'''
import pandas as pd
import csv
import dns
from sqlalchemy import create_engine
from connstring import connstr, conn_string_mongo

from pymongo import MongoClient

# Saving for when I get this script on Flask
# from flask.ext.mongoalchemy import MongoAlchemy
# https://pythonhosted.org/Flask-MongoAlchemy/

sp500_df = pd.read_csv('SP500.csv', index_col='Ticker symbol')
wanted_cols = ['Security', 'GICS Sector', 'GICS Sub Industry']
sp500_df = sp500_df[wanted_cols]
sp500_df.columns = ['Company Name', 'Sector', 'Sub Industry']

engine = create_engine(connstr)


def pull_in_stock_data(query):
    with engine.connect() as conn, conn.begin():
        return pd.read_sql(query, conn)


cols = 'timestamp, ticker, closing_price, minimum_price, maximum_price, volume'
query = 'select {} from stock_db where timestamp in (select timestamp from stock_db) order by timestamp DESC, ticker ASC'.format(cols)
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

analysis_df = pd.merge(analysis_df, sp500_df, how='inner', left_on='ticker', right_index=True)

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

df3 = df3.sort_values('growth', ascending=False).reset_index().rename(columns={'index': "Ticker"})
date = df3['date'][0]
stock_df_for_insert = df3.reset_index()
stock_df_for_insert.rename(columns={'index': 'rank'})

#####################
# sectors
#####################


sector_df = analysis_df.reset_index().copy()
sector_df = sector_df.groupby(['Sector', 'timestamp']).sum().sort_index(ascending=[True, False])

delta_percent = []


def get_percent_changes(lst):
    for companies in lst:
        company_performance = sector_df.loc[companies]['closing_price']
        today = company_performance[0]
        yesterday = company_performance[1]

        delta = (today - yesterday)
        delta_pct = (delta / yesterday) * 100
        delta_percent.append(round(delta_pct, 2))


use_lst = list(sector_df.index.levels[0])
get_percent_changes(use_lst)

data = {'pct_delta': delta_percent}


sector_df_for_insert = pd.DataFrame(data, index=use_lst).sort_values('pct_delta', ascending=False).reset_index()
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
