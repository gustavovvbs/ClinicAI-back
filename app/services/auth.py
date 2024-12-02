from datetime import datetime, timedelta
import os
from flask import current_app
from app.models.user import UserModel
from app.schemas.auth import UserCreateSchema, UserLoginSchema
from app.core.security import hash_password, verify_password
from jose import jwt, JWTError
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

class AuthService:
    def __init__(self):
        self.db = current_app.mongo
        self.ACCESS_TOKEN_EXPIRE_DAYS = 7
        self.SECRET_KEY = os.getenv("SECRET_KEY")

    def _get_user_by_id(self, user_id: str):
        return self.db.users.find_one({
            "_id": ObjectId(user_id)
        })

    def register(self, user_data: dict):
        existing_user = self.db.users.find_one({"email": user_data["email"]})
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = hash_password(user_data["password"])
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
        )

        result = self.db.users.insert_one(user.model_dump())
        return {"user_id": str(result.inserted_id)}

    def login(self, user_data: dict):
        user = self.db.users.find_one({"email": user_data["email"]})
        if not user:
            raise ValueError("User not found")

        if not verify_password(user_data['password'], user["hashed_password"]):
            raise ValueError("Invalid password")

        access_token = self._create_token(
            data={"sub": str(user["_id"])},
            expires_delta=timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS),
        )

        return {"access_token": access_token, "token_type": "bearer"}

    def _create_token(self, data: dict, expires_delta: timedelta):
        """
        Create a new JWT token with the given data and expiration time.

        Args:
            data (dict): Data to encode in the token.
            expires_delta (timedelta): Time delta for the token to expire.

        Returns:
            str: The encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm="HS256")

    def verify_token(self, token: str):
        """
        Verify a JWT token and returns if the user exists.

        Args:
            token (str): The token to verify.

        Returns:
            bool: Boolean indicating the validity of the jwt token.
        
        Raises:
            ValueError: If the token is invalid.
        """
        try:
                payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("sub")
                if user_id is None:
                    raise ValueError("Invalid token")

                found_user = self._get_user_by_id(user_id)
                if not found_user:
                    return False
            
                return True
        except JWTError:
            raise ValueError("Invalid token")
