from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, engine
import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="SecureChat")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# Demo-only in-memory data. Replace with your SQL/database layer.
demo_threads = [
    {"id": 1, "name": "Thread 01", "status": "Connected", "time": "2m", "active": True},
    {"id": 2, "name": "Thread 02", "status": "Offline", "time": "15m", "active": False},
    {"id": 3, "name": "Thread 03", "status": "Offline", "time": "1h", "active": False},
    {"id": 4, "name": "Thread 04", "status": "Offline", "time": "2h", "active": False},
    {"id": 5, "name": "Thread 05", "status": "Offline", "time": "1d", "active": False},
]

demo_messages = [
    {"sender": "other", "text": "Public key received. Secure session started."},
    {"sender": "me", "text": "Connection confirmed."},
    {"sender": "other", "text": "Messages are encrypted before storage."},
    {"sender": "me", "text": "Sounds good. Sending a test message now."},
]


@app.get("/")
def root():
    return RedirectResponse(url="/login")


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"title": "Log in"}
    )


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    # Replace this with real authentication.
    return RedirectResponse(url="/chat", status_code=303)


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"title": "Create account"}
    )


@app.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Replace this with password hashing + public key registration.
    return RedirectResponse(url="/login", status_code=303)


@app.get("/chat")
def chat_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "title": "Chat",
            "username": "Baron",
            "threads": demo_threads,
            "messages": demo_messages,
            "active_thread": demo_threads[0],
        },
    )


@app.post("/send")
def send_message(message: str = Form(...)):
    # Replace this with encrypted message handling + database insert.
    return RedirectResponse(url="/chat", status_code=303)
