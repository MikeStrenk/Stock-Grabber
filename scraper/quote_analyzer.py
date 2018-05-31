'''
This python script pulls the most recent couple days of stock performance from
a database and inserts the following into another MongoDB:
- Top 5 stocks that grew, and %
- Worst 5 stocks, and %
- Top 3 sectors that grew, and %
- Worst 3 sectors, and %
'''
import pandas as pd
from sqlalchemy import create_engine

from connstring import connstr

engine = create_engine(connstr)

sql_query = 'select * from stock_db;'


def pull_in_stock_data(query):
    with engine.connect() as conn, conn.begin():
        return pd.read_sql(query, conn)


stocks_df = pull_in_stock_data(sql_query)
