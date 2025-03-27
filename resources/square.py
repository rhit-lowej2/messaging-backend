# resources/square.py
# This file defines a simple resource to calculate the square of a number.

from flask import jsonify
from flask_restful import Resource

class Square(Resource):
    def get(self, num):
        # Return the square of the provided number.
        return jsonify({'square': num ** 2})
        