import hashlib
import os

USERS_FILE = "users.txt"

def hash_password(password):
    """Hashes a password using SHA-256."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt + key

def verify_password(password, hashed_password):
    """Verifies a password against a hashed password."""
    salt = hashed_password[:32]
    key = hashed_password[32:]
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return new_key == key

def register(username, password):
    """Registers a new user with the given username and password."""
    with open(USERS_FILE, "a") as f:
        hashed_password = hash_password(password)
        f.write(f"{username}:{hashed_password.hex()}\n")

def authenticate(username, password):
    """Authenticates a user with the given username and password."""
    with open(USERS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if parts[0] == username:
                hashed_password = bytes.fromhex(parts[1])
                if verify_password(password, hashed_password):
                    return True
                else:
                    return False
    return False

