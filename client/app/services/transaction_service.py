from urllib import parse

from services.api import auth_headers, delete_request, post_json, put_json, send_request
from services.auth_service import get_token


def build_query(params):
    clean_params = {key: value for key, value in params.items() if value not in (None, "")}
    return parse.urlencode(clean_params)


def get_transactions(filters=None):
    filters = filters or {}
    query = build_query(filters)
    path = "/transactions/"
    if query:
        path = f"{path}?{query}"
    return send_request(path, headers=auth_headers(get_token()))


def create_transaction(data, ignore_budget_limit=False):
    path = "/transactions/"
    if ignore_budget_limit:
        path = f"{path}?ignore_budget_limit=true"
    return post_json(path, data, headers=auth_headers(get_token()))


def update_transaction(transaction_id, data):
    return put_json(f"/transactions/{transaction_id}", data, headers=auth_headers(get_token()))


def delete_transaction(transaction_id):
    return delete_request(f"/transactions/{transaction_id}", headers=auth_headers(get_token()))


def get_category_stats(month=None, year=None, transaction_type=None):
    query = build_query({
        "month": month,
        "year": year,
        "transaction_type": transaction_type,
    })
    path = "/transactions/stats"
    if query:
        path = f"{path}?{query}"
    return send_request(path, headers=auth_headers(get_token()))


def get_monthly_stats(limit_months=6):
    query = build_query({"limit_months": limit_months})
    return send_request(f"/transactions/monthly-stats?{query}", headers=auth_headers(get_token()))
