from pymongo.son_manipulator import SONManipulator
from bson import SON

class AutoCast(SONManipulator):
    """
    Auto object casting to get back right object
    """
    def transform_outgoing(self, son, collection):
        return son