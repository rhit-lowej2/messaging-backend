# resources/messages.py
# This file defines messaging resources:
# DirectMessage, GetDirectMessages, PublicMessage, GetPublicMessages, and GroupMessage.

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId
from db import get_db

# For messaging, we use a separate collection named 'messages' in the default database.
db = get_db()

class DirectMessage(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'recipient_id' not in data or 'content' not in data:
            return make_response(jsonify({"error": "recipient_id and content are required"}), 400)
        
        sender_id = get_jwt_identity()
        recipient_id = data['recipient_id']
        content = data['content']
        
        message = {
            "sender_id": ObjectId(sender_id),
            "recipient_id": ObjectId(recipient_id),
            "message_type": "direct",
            "content": content,
            "timestamp": datetime.utcnow()
        }
        db.messages.insert_one(message)
        return make_response(jsonify({"message": "Direct message sent successfully"}), 201)

class GetDirectMessages(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        recipient_id = request.args.get("recipient_id")
        if not recipient_id:
            return make_response(jsonify({"error": "Missing recipient_id parameter"}), 400)
        
        messages_cursor = db.messages.find({
            "message_type": "direct",
            "$or": [
                {"sender_id": ObjectId(user_id), "recipient_id": ObjectId(recipient_id)},
                {"sender_id": ObjectId(recipient_id), "recipient_id": ObjectId(user_id)}
            ]
        }).sort("timestamp", 1)
        
        messages = []
        for msg in messages_cursor:
            sender_info = db.users.find_one(
                {"_id": msg["sender_id"]},
                {"username": 1, "_id": 0}  
            )
            sender_username = sender_info["username"] if sender_info else "Unknown"
            messages.append({
                "sender_id": str(msg["sender_id"]),
                "sender_username": sender_username,
                "recipient_id": str(msg["recipient_id"]),
                "content": msg["content"],
                "timestamp": msg["timestamp"].isoformat()
            })
        return make_response(jsonify({"messages": messages}), 200)

class PublicMessage(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'content' not in data:
            return make_response(jsonify({"error": "Content field is required"}), 400)
        
        sender_id = get_jwt_identity()
        content = data['content']
        tags = data.get('tags', [])
        
        message = {
            "sender_id": ObjectId(sender_id),
            "message_type": "public",
            "content": content,
            "tags": tags,
            "timestamp": datetime.utcnow()
        }
        db.messages.insert_one(message)
        return make_response(jsonify({"message": "Public message sent successfully"}), 201)

class GetPublicMessages(Resource):
    def get(self):
        tag_filter = request.args.get("tag")
        query = {"message_type": "public"}
        if tag_filter:
            query["tags"] = tag_filter
        
        messages_cursor = db.messages.find(query).sort("timestamp", -1)
        messages = []
        for msg in messages_cursor:
            sender_info = db.users.find_one(
                {"_id": msg["sender_id"]},
                {"username": 1, "_id": 0}
            )
            sender_username = sender_info["username"] if sender_info else "Unknown"

            messages.append({
                "sender_id": str(msg["sender_id"]),
                "sender_username": sender_username,
                "content": msg["content"],
                "tags": msg.get("tags", []),
                "timestamp": msg["timestamp"].isoformat()
            })
        return make_response(jsonify({"messages": messages}), 200)

class GroupMessage(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'group_id' not in data or 'content' not in data:
            return make_response(jsonify({"error": "group_id and content are required"}), 400)
        
        sender_id = get_jwt_identity()
        group_id = data['group_id']
        content = data['content']
        
        # Optionally, you can check if the sender belongs to the group.
        message = {
            "sender_id": ObjectId(sender_id),
            "group_id": ObjectId(group_id),
            "message_type": "group",
            "content": content,
            "timestamp": datetime.utcnow()
        }
        db.messages.insert_one(message)
        return make_response(jsonify({"message": "Group message sent successfully"}), 201)

class GetGroupMessages(Resource):
    @jwt_required()
    def get(self, group_id):
        messages_cursor = db.messages.find({
            "message_type": "group",
            "group_id": ObjectId(group_id)
        }).sort("timestamp", 1)
        
        messages = []
        for msg in messages_cursor:
            sender_info = db.users.find_one(
                {"_id": msg["sender_id"]},
                {"username": 1, "_id": 0}
            )
            sender_username = sender_info["username"] if sender_info else "Unknown"

            messages.append({
                "sender_id": str(msg["sender_id"]),
                "sender_username": sender_username,
                "content": msg["content"],
                "timestamp": msg["timestamp"].isoformat()
            })
        return make_response(jsonify({"messages": messages}), 200)
