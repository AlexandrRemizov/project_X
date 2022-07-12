import base64
import hashlib
import hmac
import json
from typing import Optional
from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = "4702300da3ca474b6ee584ec7937c90c1601e1c909ecfe2cfa6725a95d705cc7"
PASSWORD_SALT = "651842cb7309d1da65adbe1d6214c6a56acf291baa3ece11f3e3a98da8af33ac"

def sign_data(data: str) -> str:
    '''Возвращает подписанные данные data'''
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split('.')
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest().lower()
    stored_password_hash = users[username]['password'].lower()
    return stored_password_hash == password_hash

users = {
    "alexandr@user.com": {
        "name": "Александр",
        "password": "e148432114a403b25e4d9e92d6da1eecbb6dd60ef134482ca085d5ac01820b7a",
        "balance": 100000
    },
    "petrpidr@user.com": {
        "name": "Петр",
        "password": "fd9e961395c7d39b85ab82469e310edb465bedfecd6ea2536769200071aeb4b7",
        "balance": 555555
    }
}

@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('html/login.html', 'r') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key='username')
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response
    return Response(f'Привет, {users[valid_username]["name"]}!<br/>'
                    f'Баланс: {users[valid_username]["balance"]}',
                    media_type="text/html")


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    print(username, password)
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
            json.dumps({
                "success": False,
                "messages": "Я вас не знаю!"
            }),
            media_type="application/json")
    response = Response(
        json.dumps({
            "success": True,
            "message": f"Привет, {user['name']}!<br/>Баланс: {user['balance']}"
        }),
        media_type="application/json")
    username_signed = base64.b64encode(username.encode()).decode() + '.' + \
                      sign_data(username)
    response.set_cookie(key='username', value=username_signed)
    return response