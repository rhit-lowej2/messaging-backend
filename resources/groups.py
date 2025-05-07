# resources/groups.py
# This file defines group-related resources, such as creating a group.

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId
from db import get_db

# Use the default database; group info will be stored in the 'groups' collection.
db = get_db()

class CreateGroup(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'group_name' not in data or 'members' not in data:
            return make_response(jsonify({"error": "group_name and members are required"}), 400)
        
        creator_id = get_jwt_identity()
        group_name = data['group_name']
        
        # Convert member IDs (strings) to ObjectId and ensure the creator is included.
        members = [ObjectId(mid) for mid in data['members']]
        if ObjectId(creator_id) not in members:
            members.append(ObjectId(creator_id))
        
        group = {
            "group_name": group_name,
            "members": members,
            "created_by": ObjectId(creator_id),
            "created_at": datetime.utcnow()
        }
        result = db.groups.insert_one(group)
        return make_response(jsonify({"message": "Group created successfully", "group_id": str(result.inserted_id)}), 201)

class GetGroups(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        groups = db.groups.find({"members": ObjectId(user_id)})
        out = []
        for group in groups:
            out.append({
                "group_id": str(group["_id"]),
                "group_name": group["group_name"],
                "members": [str(member) for member in group["members"]],
                "created_by": str(group["created_by"]),
                "created_at": group["created_at"]
            })
        return make_response(jsonify({"groups": out}), 200)


class CreateDM(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'recipient' not in data:
            return make_response(jsonify({"error": "recipient required"}), 400)

        creator_id = get_jwt_identity()
        recipient = data['recipient']
        recipient_id = db.users.find_one({'username': recipient})

        if not recipient_id:
            return make_response(jsonify({"error": "recipient not found"}), 400)

        # Convert member IDs (strings) to ObjectId and ensure the creator is included.
        members = [ObjectId(recipient_id["_id"])]
        if ObjectId(creator_id) not in members:
            members.append(ObjectId(creator_id))

        dm = {
            "members": members,
            "created_by": ObjectId(creator_id),
            "created_at": datetime.utcnow()
        }
        result = db.dms.insert_one(dm)
        return make_response(jsonify({"message": "Direct message created successfully", "dm_id": str(result.inserted_id)}),
                             201)


class GetDMs(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        dms = db.dms.find({"members": ObjectId(user_id)})
        out = []
        for dm in dms:
            for member in dm["members"]:
                if member != ObjectId(user_id):
                    recipient = db.users.find_one({'_id': member})
                    out.append({
                        "recipient_id": str(recipient["_id"]),
                        "recipient": recipient["username"],
                        "created_by": str(dm["created_by"]),
                        "created_at": dm["created_at"]
                    })
        return make_response(jsonify({"dms": out}), 200)

