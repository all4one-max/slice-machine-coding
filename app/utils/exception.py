from fastapi import HTTPException


class RandomException(Exception):
    pass


class UserDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User does not exist")
