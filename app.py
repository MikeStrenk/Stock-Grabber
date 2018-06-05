#!flask/bin/python
from flask import Flask, jsonify, abort, request, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient

from connstring import conn_string_mongo

app = Flask(__name__)

# Need to configure these
# app.config['MONGO_DBNAME'] = 'restdb'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)


def get_sector_data():
    client = MongoClient(conn_string_mongo)
    db = client.test_database
    sectorData = db.sectorData
    return sectorData.find_one()


@app.route('/')
def return_index_page():
    return render_template('index.html')


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


if __name__ == '__main__':
    app.run(debug=True)
