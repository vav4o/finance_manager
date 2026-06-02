from services.api import auth_headers, delete_request, post_json, send_request
from services.auth_service import get_token


def get_categories():
    return send_request("/categories/", headers=auth_headers(get_token()))


def create_category(data):
    return post_json("/categories/", data, headers=auth_headers(get_token()))


def delete_category(category_id):
    return delete_request(f"/categories/{category_id}", headers=auth_headers(get_token()))
