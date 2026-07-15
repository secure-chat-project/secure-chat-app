import requests
import crypto

SERVER_URL = "https://securechat.chickenkiller.com"

def initialize_keys(session_cookie):
    if not crypto.keypair_exists():
        print("No keypair found, generating new RSA-2048 keypair...")
        private_key = crypto.generate_keypair()
        crypto.save_private_key(private_key)
        crypto.save_public_key(private_key)
        print("Keypair generated and saved")
    else:
        print("Keypair already exists, skipping generation")

    upload_public_key(session_cookie)

def upload_public_key(session_cookie):
    public_key_pem = crypto.get_public_key_pem()

    response = requests.post(
        f"{SERVER_URL}/keys/upload",
        data={"public_key": public_key_pem},
        cookies={"access_token": session_cookie}
    )

    result = response.json()
    if result["success"]:
        print("Public key uploaded successfully")
    else:
        print(f"Key upload failed: {result['message']}")

def fetch_peer_public_key(username):
    response = requests.get(f"{SERVER_URL}/keys/fetch/{username}")
    result = response.json()

    if result["success"]:
        return result["public_key"]
    else:
        print(f"Could not fetch key for {username}: {result['message']}")
        return None