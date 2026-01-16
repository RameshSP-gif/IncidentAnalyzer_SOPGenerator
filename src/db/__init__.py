"""Database module for MongoDB integration"""

from .mongodb_handler import MongoDBHandler, get_mongodb_handler

__all__ = ['MongoDBHandler', 'get_mongodb_handler']
