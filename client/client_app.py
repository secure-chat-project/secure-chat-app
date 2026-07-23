from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import messaging
import key_manager
import crypto

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER_URL = "https://securechat.chickenkiller.com"

session = {
    "cookie": None,
    "username": None
}

@app.post("/local/login")
def local_login(username: str = Form(...), password: str = Form(...)):
    response = requests.post(
        f"{SERVER_URL}/login",
        data={"username": username, "password": password},
        allow_redirects=False
    )
    cookie = response.cookies.get("access_token")
    if not cookie:
        return JSONResponse({"success": False, "message": "Invalid credentials"})

    session["cookie"] = cookie
    session["username"] = username
    key_manager.initialize_keys(cookie)

    return JSONResponse({"success": True, "username": username})


@app.post("/local/send")
def local_send(recipient: str = Form(...), message: str = Form(...)):
    if not session["cookie"]:
        return JSONResponse({"success": False, "message": "Not logged in"})

    success = messaging.send_message(recipient, message, session["cookie"])
    return JSONResponse({"success": success})


@app.get("/local/history")
def local_history():
    if not session["cookie"]:
        return JSONResponse({"success": False, "message": "Not logged in"})

    messages = messaging.get_history(session["cookie"], session["username"])
    return JSONResponse({"success": True, "messages": messages})


@app.get("/local/users")
def local_users():
    response = requests.get(f"{SERVER_URL}/users")
    return JSONResponse(response.json())


@app.get("/local/whoami")
def whoami():
    return JSONResponse({
        "username": session["username"],
        "logged_in": session["cookie"] is not None
    })