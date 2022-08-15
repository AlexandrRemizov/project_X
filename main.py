import base64
import hashlib
import hmac
import json
from typing import Optional
from fastapi import FastAPI, Form, Cookie, Body
from fastapi.responses import Response
from os import environ
import databases
from routers import users

DB_USER = environ.get("DB_USER", "user")
DB_PASS = environ.get("DB_PASS", "password")
DB_HOST = environ.get("DB_HOST", "localhost")
DB_NAME = "postgres"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
)
database = databases.Database(SQLALCHEMY_DATABASE_URL)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(users.router)

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
    user = users.get(username)
    if not user or not verify_password(username, password):
        response = Response(
            json.dumps({
                "success": False,
                "messages": "Я вас не знаю!"
            }),
            media_type="application/json")
        return response
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