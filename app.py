#!flask/bin/python
from datetime import datetime
from flask import Flask, jsonify, abort, request, render_template, redirect
from flask_pymongo import PyMongo
import os
from pymongo import MongoClient

# Use the os.environ for Heroku and import for local development
conn_string_mongo = os.environ.get('conn_string_mongo')
# from connstring import conn_string_mongo

app = Flask(__name__)

client = MongoClient(conn_string_mongo)
db = client.test_database
stockData = db.stockData
sectorData = db.sectorData

date_obj = stockData.find({},
                          {'date': 1,
                           '_id': 0}).sort([('date', -1)]).limit(1)

def get_stock_data(sort_direction, count=5):
    '''sort_direction should be -1 for best stocks, 1 for worst stocks'''
    date_obj = stockData.find({},
                              {'date': 1,
                               '_id': 0}).sort([('date', -1)]).limit(1)
    date_dict = {}
    for items in date_obj:
        date_dict['date'] = items['date']

    stock_data = stockData.find({'date': date_dict['date']},
                                {'date': 1,
                                 '_id': 0,
                                 'Ticker': 1,
                                 'Company': 1,
                                 'quote price': 1,
                                 'growth': 1}).sort([('growth',
                                                      sort_direction)])

    stock_data_container = []
    for items in stock_data:
        stock_data_container.append(items)

    return stock_data_container[:count]


def get_sector_data():
    data = sectorData.find_one()
    ranking = {}
    for items in data['data']:
        rank = items['Rank']
        name = items['Sector']
        delta = items['pct_delta']
        ranking.update({rank: {'name': name, 'delta': delta}})
    return ranking


@app.route('/')
def return_index_page():
    best_stocks = get_stock_data(sort_direction=-1)
    worst_stocks = get_stock_data(sort_direction=1)
    daily_sector_ranking = get_sector_data()
    return render_template('index.html', date_obj=date_obj,
                           best_stock_ranking=best_stocks,
                           worst_stock_ranking=worst_stocks,
                           daily_sector_ranking=daily_sector_ranking
                           )


@app.route('/', methods=['POST'])
@app.route('/<ticker>', methods=['POST'])
def test(ticker=''):
    text = request.form['search']
    return redirect('/'+text)


@app.route('/<ticker>')
def ticker_search(ticker):
    date_obj = stockData.find({},
                              {'date': 1,
                               '_id': 0}).sort([('date', -1)]).limit(1)

    date_dict = {}
    for items in date_obj:
        date_dict['date'] = items['date']

    stock_data = stockData.find_one({'date': date_dict['date'],
                                     'Ticker': ticker},
                                    {'date': 1,
                                     '_id': 0,
                                     'Ticker': 1,
                                     'Company': 1,
                                     'quote price': 1,
                                     'growth': 1})

    if stock_data == None:
        stock_date = {"date": ''}

        stock_list = ''
        # data = stockData.distinct({'Ticker'})
                                     # .sort([('Ticker', 1)])
        # for item in data:
        #     stock_list += '<p>' + item['Ticker'] + ': ' + item['Company'] + '</p>'

        return render_template('404.html', stock_list=stock_list), 404
    else:
        stock_date = 'Last Updated: ' + str(stock_data['date'].strftime('%I:%M %p Central, %A'))
        return render_template('quote.html',
                           stock_data=stock_data,
                           stock_date=stock_date)


if __name__ == '__main__':
    app.run(debug=False)
