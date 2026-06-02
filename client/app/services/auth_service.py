from services.api import post_form, post_json, send_request


access_token = None


def login_user(username, password):
    global access_token

    data = {
        "username": username,
        "password": password,
    }

    response = post_form("/users/login", data)
    access_token = response["access_token"]

    return get_current_user()


def register_user(user_data):
    return post_json("/users/register", user_data)


def get_token():
    return access_token


def logout_user():
    global access_token
    access_token = None


def get_current_user():
    headers = {"Authorization": f"Bearer {access_token}"}
    return send_request("/users/me", headers=headers)
