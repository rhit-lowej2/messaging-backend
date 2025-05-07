
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
from resources.groups import CreateGroup
import os
from config import Config
import bcrypt

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from db import get_db

# creating the flask app 
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
CORS(app)
api = Api(app)
jwt = JWTManager(app)

def reset_message_counts():
    """
    Reset 'message_count' and update 'last_reset' timestamp
    for all users every 24 hours.
    """
    db = get_db()
    result = db.users.update_many(
        {},
        {
            '$set': {
                'message_count': 0,
                'last_reset': datetime.utcnow()
            }
        }
    )
    # Log how many user docs were modified
    print(f"{datetime.utcnow().isoformat()} - Reset message_count for {result.modified_count} users.")

scheduler = BackgroundScheduler()
# trigger every 24 hours
scheduler.add_job(
    func=reset_message_counts,
    trigger='interval',
    hours=24,
    id='reset_message_counts_job',
    name='Reset message_count every 24h'
)
scheduler.start()

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)