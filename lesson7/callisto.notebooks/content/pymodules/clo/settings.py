import os
from pickleshare import PickleShareDB
from clo.environment import Environment


class Settings(object):
    def __init__(self, root_dir=None, prefix=None):
        if root_dir is None:
            root_dir = Environment.settings_dir()

        if prefix is not None:
            root_dir = os.path.realpath(os.path.join(root_dir, prefix))

        self.db = PickleShareDB(root_dir)

    def root(self):
        return self.db.root

    def clear(self):
        """Remove all entries"""
        self.db.clear()

    def keys(self):
        return self.db.keys()

    def remove(self, key):
        del self.db[key]

    def set_value(self, key, value):
        """Sets the value of setting key to value."""
        self.db[key] = value

    def value(self, key, default=None):
        """Returns the value for setting key"""
        return self.db.get(key, default)
