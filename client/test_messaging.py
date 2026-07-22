import key_manager
import messaging
import requests

SERVER_URL = "https://securechat.chickenkiller.com"

def login(username, password):
    response = requests.post(
        f"{SERVER_URL}/login",
        data={"username": username, "password": password},
        allow_redirects=False
    )
    cookie = response.cookies.get("access_token")
    if cookie:
        print(f"Login successful for {username}")
        return cookie
    else:
        print("Login failed")
        return None

def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    session_cookie = login(username, password)
    if not session_cookie:
        return

    key_manager.initialize_keys(session_cookie)

    recipient = input("Enter recipient username: ")
    message = input("Enter message: ")

    messaging.send_message(recipient, message, session_cookie)

    print("\n--- Message History ---")
    history = messaging.get_history(session_cookie, username)
    for msg in history:
        print(f"[{msg['timestamp']}] {msg['sender']} → {msg['recipient']}: {msg['message']}")

if __name__ == "__main__":
    main()