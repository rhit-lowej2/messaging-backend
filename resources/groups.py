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
