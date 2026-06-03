from urllib import parse

from services.api import auth_headers, delete_request, post_json, put_json, send_request
from services.auth_service import get_token


def get_budgets(month, year):
    query = parse.urlencode({"month": month, "year": year})
    return send_request(f"/budgets/?{query}", headers=auth_headers(get_token()))


def create_budget(data):
    return post_json("/budgets/", data, headers=auth_headers(get_token()))


def update_budget(budget_id, data):
    return put_json(f"/budgets/{budget_id}", data, headers=auth_headers(get_token()))


def delete_budget(budget_id):
    return delete_request(f"/budgets/{budget_id}", headers=auth_headers(get_token()))
