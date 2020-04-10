from projects_base.base.models import ShelveObject
from bcrypt import checkpw


class Project(ShelveObject):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def serialize(self):
        return self.__dict__


class User(ShelveObject):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def serialize(self):
        return self.__dict__

    @staticmethod
    def valid_user(email, password):
        user = User.get_with_first("email", email)
        if user is not None and checkpw(bytes(password, "utf-8"), user.password):
            return user
        return None

    def is_authenticated(self):
        return self.__dict__["is_authenticated"]

    def is_active(self):
        return self.__dict__["is_active"]

    def is_anonymous(self):
        return self.__dict__["is_anonymous"]

    def get_id(self):
        return self._id
