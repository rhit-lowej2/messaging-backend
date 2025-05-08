# resources/ads.py
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from datetime import datetime
from db import get_db

ads_collection = get_db('ads')['ad_list']

class AdList(Resource):
    def get(self):
        ads = list(ads_collection.find({}, {"__v": 0}))
        for ad in ads:
            ad["_id"] = str(ad["_id"])
        return make_response(jsonify({"ads": ads}), 200)

    @jwt_required() 
    def post(self):
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return make_response(jsonify({"error": "Missing title or content"}), 400)
        new_ad = {
            "title": data["title"],
            "content": data["content"],
            "image_url": data.get("image_url", ""),
            "link": data.get("link", ""),
            "created_at": datetime.utcnow()
        }
        res = ads_collection.insert_one(new_ad)
        new_ad["_id"] = str(res.inserted_id)
        return make_response(jsonify({"ad": new_ad}), 201)

class AdFetch(Resource):
    def get(self):
        pipeline = [{"$sample": {"size": 1}}]
        result = list(ads_collection.aggregate(pipeline))
        if not result:
            return make_response(jsonify({"ad": None}), 200)
        ad = result[0]
        ad["_id"] = str(ad["_id"])
        return make_response(jsonify({"ad": ad}), 200)
