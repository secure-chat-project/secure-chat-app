from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

users = {}
messages = []

class RegisterRequest(BaseModel):
    username: str
    public_key: str

class MessageRequest(BaseModel):
    sender: str
    receiver: str
    message: str


@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Secure Chat App"
    }

@app.get("/users")
def get_users():
    return users

@app.post("/register")
def register(data: RegisterRequest):
    if data.username in users:
        return {
            "success": False,
            "message": "Username already exists",
        }

    users[data.username] = data.public_key
    return {
        "success": True,
        "message": f"User {data.username} created",
    }

@app.post("/send")
def send(data: MessageRequest):
#    if data.username not in users:
#       return {
#            "success": False,
#            "message": "User not registered",
#        }

    message = {
        "sender": data.sender,
        "receiver": data.receiver,
        "message": data.message
    }

    messages.append(message)
    print(message)

    return {
        "success": True,
        "message": "Message stored",
    }

@app.get("/messages/{username}")
def get_message(username: str):
    inbox = []

    for message in messages:
        if message["sender"] == username and message["receiver"] == username:
            inbox.append(message)

    return {
        "username": username,
        "messages": messages,
    }