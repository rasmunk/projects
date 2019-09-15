import shelve
import uuid
import fnmatch
import fcntl
from projects_base.base import app


class ShelveObject:
    def __init__(self):
        # Key Identifier
        self._id = str(uuid.uuid4())
        # Type identifier, used for retriving on the relvant instances
        self._type = str(type(self))

    def save(self):
        with open(app.config['DB_LOCK'], 'wb') as lckfile:
            # Lock before db write operation, blocking for now
            fcntl.flock(lckfile.fileno(), fcntl.LOCK_EX)
            with shelve.open(app.config['DB']) as db:
                db[self._id] = {key: self.__dict__[key] for key in
                                self.__dict__.keys()}
            # Unlock after operation
            fcntl.flock(lckfile.fileno(), fcntl.LOCK_UN)

        return self._id

    # Returns a new instance of the calling class with the same _shelve id.
    @classmethod
    def get(cls, instance_id):
        _object = None
        try:
            with shelve.open(app.config['DB']) as db:
                _object = cls(**db[instance_id])
        except KeyError:
            pass
        return _object

    # Returns a list of instances of the calling class
    @classmethod
    def get_all(cls):
        ids = []
        with shelve.open(app.config['DB']) as db:
            ids = [key for key in db.keys() if db[key]['_type'] == str(cls)]
        return [cls.get(instance_id) for instance_id in ids]

    @classmethod
    def remove(cls, shelve_id):
        with open(app.config['DB_LOCK'], 'wb') as lckfile:
            # Lock before db write operation, blocking for now
            fcntl.flock(lckfile.fileno(), fcntl.LOCK_EX)
            with shelve.open(app.config['DB']) as db:
                db.pop(shelve_id)
            # Unlock after operation
            fcntl.flock(lckfile.fileno(), fcntl.LOCK_UN)

    @classmethod
    def clear(cls):
        for instance in cls.get_all():
            cls.remove(instance._id)

    @classmethod
    def get_with_search(cls, key, value):
        result = []
        search = "*" + value + "*"
        objects = cls.get_all()
        for obj in objects:
            if hasattr(obj, key):
                if len(fnmatch.filter([obj.__dict__[key].lower()],
                                      search.lower())) > 0:
                    result.append(obj)
        return result

    @classmethod
    def get_with_first(cls, key, value):
        objects = cls.get_all()
        for obj in objects:
            if hasattr(obj, key):
                if obj.__dict__[key] == value:
                    return obj
        return None
