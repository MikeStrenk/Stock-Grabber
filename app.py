#!flask/bin/python
from datetime import datetime
from flask import Flask, jsonify, abort, request, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient

from connstring import conn_string_mongo

app = Flask(__name__)

client = MongoClient(conn_string_mongo)
db = client.test_database
stockData = db.stockData
sectorData = db.sectorData


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


@app.route('/test')
def test():
    return "test page"


@app.route('/')
def return_index_page():
    best_stocks = get_stock_data(sort_direction=-1)
    worst_stocks = get_stock_data(sort_direction=1)
    daily_sector_ranking = get_sector_data()
    return render_template('index.html',
                           best_stock_ranking=best_stocks,
                           worst_stock_ranking=worst_stocks,
                           daily_sector_ranking=daily_sector_ranking
                           )


if __name__ == '__main__':
    app.run(debug=True)

# app.run(debug=True, port=8000, host='0.0.0.0')

# tasks = [
#     {
#         'id': 1,
#         'title': u'Buy groceries',
#         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
#         'done': False
#     },
#     {
#         'id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web',
#         'done': False
#     }
# ]

# @app.route('/todo/api/v1.0/tasks', methods=['GET'])
# def get_tasks():
#     return jsonify({'tasks': tasks})
#
#
#
#
# @app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
# def get_task(task_id):
#     task = [task for task in tasks if task['id'] == task_id]
#     if len(task) == 0:
#         abort(404)
#     return jsonify({'task': task[0]})
