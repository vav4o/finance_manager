from services.api import auth_headers, delete_request, post_json, put_json, send_request
from services.auth_service import get_token


def get_accounts():
    return send_request("/accounts/", headers=auth_headers(get_token()))


def create_account(data):
    return post_json("/accounts/", data, headers=auth_headers(get_token()))


def update_account(account_id, data):
    return put_json(f"/accounts/{account_id}", data, headers=auth_headers(get_token()))


def delete_account(account_id):
    return delete_request(f"/accounts/{account_id}", headers=auth_headers(get_token()))
