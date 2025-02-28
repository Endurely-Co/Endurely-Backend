"""

"""
from rest_framework import status
from rest_framework.response import Response

from utils.validator import Status, Messages


def extract_400_error(what: str):
    return {
        "code": Status.INVALID_REQUEST,
        "message": Messages.error_400.format(what)
    }


def extract_error(what: str, code: int = Status.INVALID_REQUEST):
    return {
        "code": code,
        "message": Messages.generic_error.format(what)
    }


def check_input(values: dict):
    # err_message = ''
    # for key in values:
    #     if not values.get(key) or type(values.get(key)) is not str:
    #         err_message += '{},'.format(key)
    #
    # if len(err_message) > 0:
    #     raise KeyError(Messages.error_400.format(err_message))
    # if len(values) == 0:
    #     raise KeyError(Messages.error_400.format("{}"))
    return values


def api_success(value):
    return Response(data={"data": value}, status=Status.SUCCESS, )


def api_created_success(value):
    return Response(data={"data": value}, status=status.HTTP_201_CREATED, )


def api_error(msg: str):
    return Response(status=Status.INVALID_REQUEST, data={
        "code": Status.INVALID_REQUEST,
        "message": msg if msg else Messages.generic_error()
    })
