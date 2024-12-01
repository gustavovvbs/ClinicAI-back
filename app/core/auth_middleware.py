import os 
from dotenv import load_dotenv
from functools import wraps 
from flask import request 
from jose import JWTError, jwt
from app.services.auth import AuthService
from app.core.config import Config

load_dotenv()

def validate_token(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {"error": "Token not provided"}, 401

            token = auth_header.split(" ")[1]

            try:
                payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
                return func(*args, **kwargs)
            except JWTError:
                return {"error": "Invalid token"}, 401
    
        return wrapper