from datetime import timedelta
from app.Seller.models import *
from app.Seller.schema import *
from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
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

class SellerService :

    @staticmethod
    async def create_seller(db: Session, seller: SellerCreate):
        try :
            db_user = db.query(Seller).filter(Seller.email == seller.email).first()
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            seller_dict = seller.dict()
            seller_dict["hashed_password"] = await SellerAuthService.get_password_hash(seller.hashed_password)

            db_seller = Seller(**seller_dict)
            db.add(db_seller)
            db.commit()
            db.refresh(db_seller)

            return SellerResponse(
                id = db_seller.id , 
                loginid =  db_seller.email , 
                password =  seller.hashed_password , 
                created_at = db_seller.created_at , 
                factories = db_seller.factories, 
                products = db_seller.products
            )
        
        except SQLAlchemyError as db_error:
            db.rollback()
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def create_factory(db: Session, factory: FactoryCreate):
        try :
            db_factory = Factory(**factory.dict())
            db.add(db_factory)
            db.commit()
            db.refresh(db_factory)

            return db_factory
        except SQLAlchemyError as db_error:
            db.rollback()
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def create_location(db: Session, location: LocationCreate):
        try :
            db_location = Location(**location.dict())
            db.add(db_location)
            db.commit()
            db.refresh(db_location)
            return db_location
        
        except SQLAlchemyError as db_error:
            db.rollback()
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def create_product(db: Session, product: ProductBase):
        try :
            db_product = Product(**product.dict())
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            return db_product
        
        except SQLAlchemyError as db_error:
            db.rollback()
            raise db_error
        except HTTPException as error :
            db.rollback()
            raise error
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def get_product_by_id(db: Session, product_id: int):
        try :
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
            return product
        
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def get_product_list( db: Session ,factory_id : int , seller_id : Optional[int] = None ):
        try :
            if not factory_id :
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Factory ID is required")
            
            query = db.query(Product).filter(Product.factory_id == factory_id)
            if seller_id:
                query = query.filter(Product.seller_id == seller_id)

            products = query.all()
            return products
        
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
    @staticmethod
    async def get_product_list_for_seller( db: Session , seller : TokenData):
        try :
            seller_data = db.query(Seller).filter(Seller.email == seller.email).first()
            if not seller_data :
                raise HTTPException(status_code= 400 , detail="Seller Data Not Found")

            products = db.query(Product).filter(Product.seller_id == seller_data.id).all()
            return products
        
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def get_seller_profile(db: Session , seller : TokenData) :
        try :
            seller_data = db.query(Seller).filter(Seller.email == seller.email).first()
            if not seller_data :
                raise HTTPException(status_code= 400 , detail="Seller Data Not Found")
            
            return seller_data
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

            

       
class SellerAuthService :

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
        user = db.query(Seller).filter(Seller.email == email).first()
        print(SellerAuthService.verify_password(password, user.hashed_password))
        if not user or not SellerAuthService.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = await SellerAuthService.create_access_token(data={"mail": user.email, "name": user.name})
        await SellerAuthService.set_cookies(access_token ,60*30 , response)
        return {"access_token": access_token, "token_type": "bearer"}
    

    
