# resources/painta_compliance.py
# This file defines tools to comply with PAINTA:

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import *
from bson.objectid import ObjectId
from db import get_db

db = get_db()


class RedactMessage(Resource):
    @jwt_required()
    def post(self):
        user = db.users.find_one({'_id': ObjectId(get_jwt_identity())})
        if not user or not user['is_admin']:
            return make_response(jsonify({"error": "Bad user in redact message"}), 400)
        data = request.get_json()
        if not data or 'message_id' not in data:
            return make_response(jsonify({"error": "message_id required for redaction"}), 400)

        result = db.messages.update_one({'_id': ObjectId(data['message_id'])},
                                        {"$set": {"content": 'This message has been redacted by an administrator'}})

        # log redaction
        db.redact_logs.insert_one({'createdAt': datetime.now(tz=timezone.utc), 'admin_id': ObjectId(get_jwt_identity()),
                                   'message_id': ObjectId(data['message_id'])})

        if result.modified_count == 0:
            return make_response(jsonify({"error": "Message not found for redaction"}), 404)
        return make_response(jsonify({"message": "Message redacted successfully"}), 200)


class ReportMessage(Resource):
    @jwt_required()
    def post(self):
        user = db.users.find_one({'_id': ObjectId(get_jwt_identity())})
        if not user:
            return make_response(jsonify({"error": "Bad user in report message"}), 400)
        data = request.get_json()
        if not data or 'message_id' not in data:
            return make_response(jsonify({"error": "message_id required for report"}), 400)

        result = db.messages.update_one({'_id': ObjectId(data['message_id'])}, {"$inc": {"reports": 1}})

        # log the report in the logs collection
        message = db.messages.find_one({'_id': ObjectId(data['message_id'])})
        origin = message['sender_id']
        content = message['content']

        db.report_logs.insert_one(
            {'createdAt': datetime.now(tz=timezone.utc), 'reporter_id': ObjectId(get_jwt_identity()),
             'origin_id': origin, 'reported_message': content})

        if result.modified_count == 0:
            return make_response(jsonify({"error": "Message not found for reporting"}), 404)
        return make_response(jsonify({"message": "Message reported successfully"}), 200)


class EraseUser(Resource):
    @jwt_required()
    def post(self):
        user_id = ObjectId(get_jwt_identity())
        user = db.users.find_one({'_id': user_id})
        if not user:
            return make_response(jsonify({"error": "Bad user in erase user"}), 400)

        # # purge all sent messages
        result = db.messages.delete_many({'sender_id': user_id})
        # print(result.deleted_count)

        # # purge all dms
        result = db.dms.delete_many({'members': user_id})
        # print(result.deleted_count)

        # purge all groups
        result = db.groups.update_many({'members': user_id}, {'$pull' : {'members': user_id}})
        # print(result.modified_count)

        # purge from report logs after delay
        db.report_logs.create_index("expire_at", expireAfterSeconds=0)
        result = db.report_logs.update_many({"$or": [{'origin_id': user_id}, {'reporter_id': user_id}]}, {'$set': {"expire_at": datetime.now() + timedelta(minutes=2)}})
        # print(result.modified_count)

        # delete user
        result = db.users.delete_one({'_id': user_id})

        if result.deleted_count == 0:
            return make_response(jsonify({"message": "User not found for deletion"}), 404)
        return make_response(jsonify({"message": "User deleted successfully"}), 200)