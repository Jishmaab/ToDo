from typing import Any


def fail(error):
    error_respons = {
        'status': False,
        'message': "fail",
        'error': error

    }

    return error_respons


def success(data: Any) -> dict:
    success_message = {
        'status': True,
        'message': 'success',
        'data': data
    }
    return success_message
