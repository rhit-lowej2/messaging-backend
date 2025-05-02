
# using flask_restful
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from resources.auth import Signup, Login, Profile
from resources.messages import (DirectMessage, GetDirectMessages, PublicMessage, 
                                GetPublicMessages, GroupMessage, GetGroupMessages)
from resources.groups import CreateGroup, GetGroups, CreateDM, GetDMs
from config import Config
import bcrypt

# creating the flask app 
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
CORS(app)
api = Api(app)
jwt = JWTManager(app)

# Register authentication routes.
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Profile, '/profile')

# Register messaging routes.
api.add_resource(DirectMessage, '/message/direct')
api.add_resource(GetDirectMessages, '/messages/direct/<string:recipient_id>')
api.add_resource(PublicMessage, '/message/public')
api.add_resource(GetPublicMessages, '/messages/public')
api.add_resource(GroupMessage, '/message/group')
api.add_resource(GetGroupMessages, '/messages/group/<string:group_id>')

# Register group management routes.
api.add_resource(CreateGroup, '/group')
api.add_resource(GetGroups, '/groups')
api.add_resource(CreateDM, '/dm')
api.add_resource(GetDMs, '/dms')

# Global error handlers (optional).
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Resource not found"}), 404)

@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({"error": "Internal server error"}), 500)

if __name__ == '__main__':
    # context = ('server.crt', 'server.key')
    app.run(debug=True)