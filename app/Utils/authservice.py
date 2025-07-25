from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request, status 
from app.Seller.models import *
from app.Seller.schema import *
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") 
TIMELIMIT = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")



def get_current_user(request : Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token")  
    print(token)
    if token is None:
        raise HTTPException(status_code=401, detail="Token not found in cookies")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("mail")
        name = payload.get("name")
        if email is None or name is None:
            raise credentials_exception
        return TokenData(email=email, name=name)
    except JWTError:
        raise credentials_exception
        