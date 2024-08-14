from rest_framework.exceptions import APIException
from rest_framework import status


class MultileDeviceLoggedIn(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = ""
    default_code = "precondition_failed"

    def __init__(self, detail=None, otp=None, id=None):
        if detail is not None:
            self.detail = {"message": detail, "otp": otp, "user_id": id}
