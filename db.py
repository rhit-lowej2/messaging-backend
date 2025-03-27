# db.py
# This file initializes the MongoDB connection using pymongo
# and provides a function to switch databases freely.

from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:cq3Nbw6BFbU7GPcR@private-messaging.hk8sb.mongodb.net/?retryWrites=true&w=majority&appName=private-messaging"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Error connecting to MongoDB:", e)

default_db = client['auth']

def get_db(db_name: str = None):
    """
    Returns a database instance by name.
    If db_name is not provided, returns the default database.
    
    :param db_name: Name of the database to retrieve.
    :return: A pymongo.database.Database instance.
    """
    if db_name:
        return client[db_name]
    return default_db
