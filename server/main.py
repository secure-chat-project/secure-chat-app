from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, engine
import models
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Cookie
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(access_token: str = Cookie(None)):
    if access_token is None:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except JWTError:
        return None

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
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"title": "Log in", "error": "Invalid username or password"}
        )

    # Verify password
    if not pwd_context.verify(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"title": "Log in", "error": "Invalid username or password"}
        )

    # Create JWT token
    token_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # Set token in cookie and redirect to chat
    response = RedirectResponse(url="/chat", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="lax")
    return response

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"title": "Create account"}
    )


@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Check passwds match
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"title": "Create account", "error": "Passwords do not match"}
        )

    # Check for duplicate username
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"title": "Create account", "error": "Username already taken"}
        )

    # Hash the password and save the user
    hashed_password = pwd_context.hash(password)
    new_user = models.User(username=username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)


@app.get("/chat")
def chat_page(request: Request, current_user: str = Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "title": "Chat",
            "username": current_user,
            "threads": demo_threads,
            "messages": demo_messages,
            "active_thread": demo_threads[0],
        },
    )

@app.post("/keys/upload")
def upload_key(
        request: Request,
        public_key: str = Form(...),
        current_user: str = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(models.User).filter(models.User.username == current_user).first()
    if not user:
        return {"success": False, "message": "User not found"}

    user.public_key = public_key
    db.commit()

    return {"success": True, "message": f"Public key uploaded for {current_user}"}

@app.get("/keys/fetch/{username}")
def fetch_key(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return {"success": False, "message": "User not found"}
    if not user.public_key:
        return {"success": False, "message": "No public key found for this user"}

    return {"success": True, "public_key": user.public_key}

@app.post("/send")
def send_message(message: str = Form(...)):
    # Replace this with encrypted message handling + database insert.
    return RedirectResponse(url="/chat", status_code=303)

@app.post("/messages/send")
def send_message(
    request: Request,
    recipient: str = Form(...),
    ciphertext: str = Form(...),
    nonce: str = Form(...),
    encrypted_key_for_recipient: str = Form(...),
    encrypted_key_for_sender: str = Form(...),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user is None:
        return {"success": False, "message": "Not authenticated"}

    new_message = models.Message(
        sender=current_user,
        recipient=recipient,
        ciphertext=ciphertext,
        nonce=nonce,
        encrypted_key_for_recipient=encrypted_key_for_recipient,
        encrypted_key_for_sender=encrypted_key_for_sender
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"success": True, "message": "Message sent"}


@app.get("/messages/history")
def get_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user is None:
        return {"success": False, "message": "Not authenticated"}

    messages = db.query(models.Message).filter(
        (models.Message.sender == current_user) |
        (models.Message.recipient == current_user)
    ).order_by(models.Message.timestamp).all()

    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender": msg.sender,
            "recipient": msg.recipient,
            "ciphertext": msg.ciphertext,
            "nonce": msg.nonce,
            "encrypted_key_for_recipient": msg.encrypted_key_for_recipient,
            "encrypted_key_for_sender": msg.encrypted_key_for_sender,
            "timestamp": str(msg.timestamp)
        })

    return {"success": True, "messages": result}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return {"success": True, "users": [u.username for u in users]}