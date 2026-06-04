import json
import os
import socket
from urllib import error, parse, request


API_URL = os.getenv("FINANCE_API_URL", "http://127.0.0.1:8000")


class ApiError(Exception):
    def __init__(self, message, status=None, detail=None):
        super().__init__(message)
        self.status = status
        self.detail = detail


def send_request(path, body=None, headers=None):
    url = f"{API_URL}{path}"
    api_request = request.Request(url, data=body, headers=headers or {})

    try:
        with request.urlopen(api_request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise read_api_error(exc)
    except (TimeoutError, socket.timeout):
        raise Exception("The server did not respond in time.")
    except error.URLError:
        raise Exception("Cannot connect to the server.")


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def post_json(path, data, headers=None):
    body = json.dumps(data).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    request_headers.update(headers or {})
    return send_request(path, body=body, headers=request_headers)


def put_json(path, data, headers=None):
    body = json.dumps(data).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    request_headers.update(headers or {})

    url = f"{API_URL}{path}"
    api_request = request.Request(url, data=body, headers=request_headers, method="PUT")

    try:
        with request.urlopen(api_request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise read_api_error(exc)
    except (TimeoutError, socket.timeout):
        raise Exception("The server did not respond in time.")
    except error.URLError:
        raise Exception("Cannot connect to the server.")


def delete_request(path, headers=None):
    url = f"{API_URL}{path}"
    api_request = request.Request(url, headers=headers or {}, method="DELETE")

    try:
        with request.urlopen(api_request, timeout=8):
            return True
    except error.HTTPError as exc:
        raise read_api_error(exc)
    except (TimeoutError, socket.timeout):
        raise Exception("The server did not respond in time.")
    except error.URLError:
        raise Exception("Cannot connect to the server.")


def post_form(path, data):
    body = parse.urlencode(data).encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return send_request(path, body=body, headers=headers)


def read_error(exc):
    api_error = read_api_error(exc)
    return str(api_error)


def read_api_error(exc):
    try:
        data = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return ApiError("Something went wrong.", status=getattr(exc, "code", None))

    detail = data.get("detail", "Something went wrong.")
    message = detail

    if isinstance(detail, list):
        messages = []
        for item in detail:
            location = " ".join(str(part) for part in item.get("loc", []))
            messages.append(f"{location}: {item.get('msg')}")
        message = "\n".join(messages)
    elif isinstance(detail, dict):
        message = detail.get("message") or detail.get("description") or str(detail)

    return ApiError(str(message), status=getattr(exc, "code", None), detail=detail)
