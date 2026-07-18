import requests
import base64
import crypto
import key_manager

SERVER_URL = "https://securechat.chickenkiller.com"

def send_message(recipient, plaintext, session_cookie):
    # Fetch recipient's public key
    recipient_public_key = key_manager.fetch_peer_public_key(recipient)
    if not recipient_public_key:
        print(f"Could not fetch public key for {recipient}")
        return False

    # Generate a fresh AES session key
    session_key = crypto.generate_session_key()

    # Encrypt the message
    ciphertext, nonce = crypto.encrypt_message(plaintext, session_key)

    # Wrap session key for recipient and sender
    encrypted_key_for_recipient = crypto.wrap_key(session_key, recipient_public_key)
    sender_public_key = crypto.get_public_key_pem()
    encrypted_key_for_sender = crypto.wrap_key(session_key, sender_public_key)

    # Base64 encode binary data for transmission
    ciphertext_b64 = base64.b64encode(ciphertext).decode("utf-8")
    nonce_b64 = base64.b64encode(nonce).decode("utf-8")
    encrypted_key_for_recipient_b64 = base64.b64encode(encrypted_key_for_recipient).decode("utf-8")
    encrypted_key_for_sender_b64 = base64.b64encode(encrypted_key_for_sender).decode("utf-8")

    # Send to server
    response = requests.post(
        f"{SERVER_URL}/messages/send",
        data={
            "recipient": recipient,
            "ciphertext": ciphertext_b64,
            "nonce": nonce_b64,
            "encrypted_key_for_recipient": encrypted_key_for_recipient_b64,
            "encrypted_key_for_sender": encrypted_key_for_sender_b64
        },
        cookies={"access_token": session_cookie}
    )

    result = response.json()
    if result["success"]:
        print("Message sent successfully")
        return True
    else:
        print(f"Failed to send message: {result['message']}")
        return False


def get_history(session_cookie, current_user):
    response = requests.get(
        f"{SERVER_URL}/messages/history",
        cookies={"access_token": session_cookie}
    )

    result = response.json()
    if not result["success"]:
        print(f"Failed to fetch history: {result['message']}")
        return []

    decrypted_messages = []
    for msg in result["messages"]:
        try:
            # Decode base64 fields
            ciphertext = base64.b64decode(msg["ciphertext"])
            nonce = base64.b64decode(msg["nonce"])

            # Use the correct wrapped key depending on whether we are sender or recipient
            if msg["sender"] == current_user:
                encrypted_key = base64.b64decode(msg["encrypted_key_for_sender"])
            else:
                encrypted_key = base64.b64decode(msg["encrypted_key_for_recipient"])

            # Unwrap the session key and decrypt the message
            session_key = crypto.unwrap_key(encrypted_key)
            plaintext = crypto.decrypt_message(ciphertext, session_key, nonce)

            decrypted_messages.append({
                "sender": msg["sender"],
                "recipient": msg["recipient"],
                "message": plaintext,
                "timestamp": msg["timestamp"]
            })

        except Exception as e:
            print(f"Could not decrypt message {msg['id']}: {e}")
            continue

    return decrypted_messages