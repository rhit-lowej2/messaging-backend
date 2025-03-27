# resources/auth.py
# This file defines authentication-related resources: Signup, Login, and Profile.

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
from db import get_db
from bson.objectid import ObjectId

# Use the default database for authentication.
db = get_db()

def hash_password(password: str) -> bytes:
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    """Verify a stored password against one provided by user."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return make_response(jsonify({"error": "Missing username or password"}), 400)
        
        username = data['username']
        password = data['password']
        display_name = data.get("display_name", username)
        email = data.get("email", "")
        
        # Check if the user already exists.
        if db.users.find_one({'username': username}):
            return make_response(jsonify({"error": "User already exists"}), 409)
        
        new_user = {
            'username': username,
            'display_name': display_name,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.utcnow()
        }
        db.users.insert_one(new_user)
        return make_response(jsonify({"message": "User registered successfully"}), 201)

class Login(Resource):
    def post(self):
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return make_response(jsonify({"error": "Missing username or password"}), 400)
        
        username = data['username']
        password = data['password']
        
        user = db.users.find_one({'username': username})
        if user and check_password(password, user['password']):
            # Generate JWT token with 24-hour expiration.
            access_token = create_access_token(identity=str(user['_id']), expires_delta=timedelta(hours=24))
            return make_response(jsonify({"message": "Login successful", "access_token": access_token}), 200)
        else:
            return make_response(jsonify({"error": "Invalid username or password"}), 401)

class Profile(Resource):
    @jwt_required()
    def get(self):
        # Retrieve current user from JWT token.
        user_id = get_jwt_identity()
        user = db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if user:
            user["_id"] = str(user["_id"])
            return make_response(jsonify({"user": user}), 200)
        return make_response(jsonify({"error": "User not found"}), 404)
