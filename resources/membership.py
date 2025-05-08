# resources/membership.py
from flask import jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from db import get_db

db = get_db()

class MembershipUpgrade(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        now = datetime.utcnow()
        expire = now + timedelta(days=31)
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "is_member": True,
                "member_since": now,
                "member_expire": expire
            }}
        )
        return make_response(jsonify({
            "message": "Membership activated",
            "member_since": now.isoformat(),
            "member_expire": expire.isoformat()
        }), 200)
