import pymongo
from mongodm.son_manipulator import AutoCast
from pymongo import database

class Connection(pymongo.Connection):
#    def __getattr__(self, name):
#        """Get a database by name."""
#        db = database.Database(self, name)
##        db.add_son_manipulator(AutoCast())
#        return db
    pass