# https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api
# Link to the docs

from flask import Flask
from flask_restful import Resource, Api
import PyMongo

app = Flask(__name__)
api = Api(app)
app.config["MONGO_DBNAME"] = "students_db"
mongo = PyMongo(app, config_prefix='MONGO')

pymongo.MongoClient('mongodb+srv://stockanalyst:XLCjTqOa3bG2F5fE@mongo-stock-analysis-db-s4y1u.mongodb.net/test?retryWrites=true')


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Student(Resource):
    def get(self, registration=None, department=None):
        data = []

        if registration:
            studnet_info = mongo.db.student.find_one({"registration": registration}, {"_id": 0})
            if studnet_info:
                return jsonify({"status": "ok", "data": studnet_info})
            else:
                return {"response": "no student found for {}".format(registration)}

        elif department:
            cursor = mongo.db.student.find({"department": department}, {"_id": 0}).limit(10)
            for student in cursor:
                student['url'] = APP_URL + url_for('students') + "/" + student.get('registration')
                data.append(student)

            return jsonify({"department": department, "response": data})

        else:
            cursor = mongo.db.student.find({}, {"_id": 0, "update_time": 0}).limit(10)

            for student in cursor:
                print student
                student['url'] = APP_URL + url_for('students') + "/" + student.get('registration')
                data.append(student)

            return jsonify({"response": data})

    def post(self):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            registration = data.get('registration')
            if registration:
                if mongo.db.student.find_one({"registration": registration}):
                    return {"response": "student already exists."}
                else:
                    mongo.db.student.insert(data)
            else:
                return {"response": "registration number missing"}

        return redirect(url_for("students"))

    def put(self, registration):
        data = request.get_json()
        mongo.db.student.update({'registration': registration}, {'$set': data})
        return redirect(url_for("students"))

    def delete(self, registration):
        mongo.db.student.remove({'registration': registration})
        return redirect(url_for("students"))


class Index(Resource):
    def get(self):
        return redirect(url_for("students"))




api = Api(app)

api.add_resource(HelloWorld, '/')
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Student, "/api", endpoint="students")
api.add_resource(Student, "/api/<string:registration>", endpoint="registration")
api.add_resource(Student, "/api/department/<string:department>", endpoint="department")

if __name__ == "__main__":
    app.run(debug=True)
