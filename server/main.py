from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

users = {}

class RegisterRequest(BaseModel):
    username: str
    public_key: str

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Secure Chat App"
    }

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
