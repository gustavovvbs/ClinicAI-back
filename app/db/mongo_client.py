from pymongo import MongoClient 
from flask import current_app
from app.core.config import Config

def init_db(app):
    client = MongoClient(Config.MONGO_URI)
    collection = client['sprint-hsl']
    app.mongo = collection
