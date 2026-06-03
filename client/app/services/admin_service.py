from services.api import auth_headers, put_json, send_request
from services.auth_service import get_token


def get_users():
    return send_request("/admin/users", headers=auth_headers(get_token()))


def toggle_user_block(user_id):
    return put_json(f"/admin/users/{user_id}/block", {}, headers=auth_headers(get_token()))


def get_system_statistics():
    return send_request("/admin/statistics", headers=auth_headers(get_token()))
