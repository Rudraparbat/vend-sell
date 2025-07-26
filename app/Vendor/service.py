from cmath import acos, cos, sin
from datetime import timedelta
from math import radians

from sqlalchemy import func
from app.Vendor.models import *
from app.Vendor.schema import *
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request, Response, status 
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from math import radians, cos, sin, acos
from geopy.geocoders import Nominatim
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
load_dotenv()


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") 
TIMELIMIT = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


class VendorService :
    @staticmethod
    async def create_vendor_user(db: Session, vendor: VendorUserCreate , response : Response):
    # Check if email already exists
        try :
            existing_vendor = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if existing_vendor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password
            hashed_password = bcrypt.hashpw(vendor.password.encode('utf-8'), bcrypt.gensalt())
            
            # Create new vendor user
            db_vendor = Vendoruser(
                name=vendor.name,
                email=vendor.email,
                password=hashed_password.decode('utf-8'),
                phone=vendor.phone
            )
            db.add(db_vendor)
            db.commit()
            db.refresh(db_vendor)

            # Direct Authentication
            access_token = await VendorAuthService.create_access_token(data={"mail": vendor.email, "name": vendor.name})
            await VendorAuthService.set_cookies(access_token ,60*30 , response)


            return VendoruserCreateResponse(
                name = db_vendor.name , 
                loginid = db_vendor.email , 
                password = vendor.password
            ) 
        
        except SQLAlchemyError  as db_error :
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def create_vendor_location(db: Session, location: VendorLocationCreate , vendor):
    # Verify shop exists
        try :
            vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Is Not Applicable"
                )
            
            location_dict = location.dict()
            location_dict["vendor_id"] = vendor_detail.id
            
            # Create new location
            db_location = VendorShopLocation(**location_dict)
            db.add(db_location)
            db.commit()
            db.refresh(db_location)
            return db_location
        
        except SQLAlchemyError  as db_error :
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def save_vendor_shop_details(db: Session, shop: VendorShopCreate , vendor):
    # Verify Detail Exist
        try :
            vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Is Not Applicable"
                )
            
            shop_dict = shop.dict()
            shop_dict["vendor_id"] = vendor_detail.id
            
            # Create new Vendor Shop
            db_shop = VendorShopDetail(**shop_dict)
            db.add(db_shop)
            db.commit()
            db.refresh(db_shop)
            return db_shop
                
        except SQLAlchemyError  as db_error :
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
    
    @staticmethod
    async def vendor_profile(db : Session , vendor) :
        try :
            if vendor is None :
                raise HTTPException(status_code= 400 , detail="Error in User Details")
            
            vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Not Found"
                )
            
            return vendor_detail

        except SQLAlchemyError  as db_error :
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))

        

class VendorAuthService :

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    async def create_access_token(data: dict):
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=int(TIMELIMIT))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def set_cookies(token , max_age , response) :

        response.set_cookie(
        key="access_token",
        value=str(token),
        httponly=True,          
        secure=True,           
        samesite="None",         
        max_age=max_age    
    )

    
    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str , response):
        user = db.query(Vendoruser).filter(Vendoruser.email == email).first()
        
        if not user or not VendorAuthService.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = await VendorAuthService.create_access_token(data={"mail": user.email, "name": user.name})
        await VendorAuthService.set_cookies(access_token ,60*30 , response)

        return {"access_token": access_token, "token_type": "bearer"}
    
    @staticmethod
    async def logout(response: Response):
        """
        Logs out the vendor by clearing the authentication cookie.
        """
        try :
            response.delete_cookie(key="access_token")
            return {
                "Status" : True ,
                "Message" : "User Logged Out Sucessfully"
            }
        
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
        
    
    @staticmethod
    async def vendor_status(db : Session , request : Request) :
        try :
            token = request.cookies.get("access_token")  
            print(token)
            is_login = True
            if token is None:
                is_login = False

            return VendorStatusSChema(
                is_login = is_login
            )        
        
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
        
    

        