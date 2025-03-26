
# using flask_restful
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import bcrypt

uri = "mongodb+srv://admin:cq3Nbw6BFbU7GPcR@private-messaging.hk8sb.mongodb.net/?retryWrites=true&w=majority&appName=private-messaging"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

auth = client['auth']


# creating the flask app 
app = Flask(__name__)
cors = CORS(app)
# creating an API object 
api = Api(app)

# making a class for a particular resource 
# the get, post methods correspond to get and post requests 
# they are automatically mapped by flask_restful. 
# other methods include put, delete, etc. 
class Login(Resource):
    def post(self):
        data = request.get_json()

        user = data.get('username')
        password = data.get('password').encode('utf-8')

        if user and password:
            out = auth.users.find_one({'username': user})
            if out and bcrypt.checkpw(password, out['password']):
                return make_response(jsonify({'login': True}), 200)

        return make_response(jsonify({'error': "Failed to login"}), 409)


class Signup(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return make_response(jsonify({"error": "Missing username or password"}), 400)

        username = data['username']
        password = data['password'].encode('utf-8')

        if auth.users.find_one({'username': username}):
            return make_response(jsonify({"error": "User already exists"}), 409)

        auth.users.insert_one({'username': username, 'password': bcrypt.hashpw(password, bcrypt.gensalt())})

        return make_response(jsonify({"message": "User created successfully"}), 201)

# another resource to calculate the square of a number 
class Square(Resource):

    def get(self, num):

        return jsonify({'square': num ** 2})


    # adding the defined resources along with their corresponding urls
api.add_resource(Login, '/login')
api.add_resource(Square, '/square/<int:num>')
api.add_resource(Signup, '/signup')


# driver function 
if __name__ == '__main__':

    app.run(debug = True) 