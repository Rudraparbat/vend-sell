from cmath import acos, cos, sin
from datetime import timedelta
from math import radians

from fastapi.responses import JSONResponse
from sqlalchemy import func
from app.Seller.models import Factory, Product, Seller
from app.Vendor.models import *
from app.Vendor.schema import *
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request, Response, status 
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import requests
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
        try:
            response = JSONResponse(content={"Status": True, "Message": "User Logged Out Successfully"})
            response.delete_cookie(key="access_token", path="/", secure=True, samesite="none")
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    # Google Auth For Sign Up
    @staticmethod
    async def google_auth_service(request : Request , code : OauthCode) :
        try :
            if not code:
                return JSONResponse({"error": "Missing code"}, status_code=400)

            # Exchange code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
                "grant_type": "authorization_code"
            }
            token_response = requests.post(token_url, data=token_data)
            if not token_response.ok:
                return JSONResponse({"error": "Token exchange failed"}, status_code=400)

            tokens = token_response.json()
            access_token = tokens.get("access_token")
            if not access_token:
                return JSONResponse({"error": "No access token"}, status_code=400)

            # Fetch user info
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_response = requests.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if not userinfo_response.ok:
                return JSONResponse({"error": "Failed to fetch user info"}, status_code=400)

            userinfo = userinfo_response.json()
            print(userinfo)
            return JSONResponse(userinfo)
        
        except HTTPException as http_error :
            raise http_error
        
        except SQLAlchemyError as db_error :
            raise db_error
        
        except Exception as e :
            raise HTTPException(status_code=500 , detail= str(e))
        
    @staticmethod
    async def vendor_status(db : Session , request : Request) :
        try :
            token = request.cookies.get("access_token")  
            print(token)

            # for profile details
            is_login = False
            profile_dones = 0
            profile_creds = []

            # for seller details 
            is_Seller = False
            seller_profile_dones = 0
            seller_profile_creds  = []

            profile_count = 0
            seller_profile_count = 0

            if token :
                is_login = True
                profile_count += 1
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("mail")

                vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == email).first()

                # add vendor details data
                if vendor_detail.shops :
                    profile_count += 1
                else :
                    profile_creds.append("shop")

                if vendor_detail.locations :
                    profile_count += 1
                else :
                    profile_creds.append("location")
                
                profile_dones = (profile_count / 3 ) * 100
                
                seller_detail = db.query(Seller).filter(Seller.vendor_id == vendor_detail.id).first() 

                if seller_detail :
                    seller_profile_count += 1
                    is_Seller = True

                    if seller_detail.factories:
                        seller_profile_count += 1
                        if all(factory.location for factory in seller_detail.factories):
                            seller_profile_count += 1
                        else:
                            seller_profile_creds.append("location")
                    else:
                        seller_profile_creds.append("factories")
                        seller_profile_creds.append("location")

                    if seller_detail.products :
                        seller_profile_count += 1
                    else :
                        seller_profile_creds.append("products")

                    
                    seller_profile_dones = (seller_profile_count / 4) * 100
                

            return VendorStatusSChema(
                is_login = is_login ,   # TO check if the user is log in or not
                is_seller = is_Seller,  # To check the user have seller account or not
                profile_done =  int(profile_dones),  # if have account how much the account creation is done 
                profile_creds =  profile_creds ,  # which part of the profile creation are pending
                seller_profile_done = int(seller_profile_dones) , # How much seller account creation is done
                seller_profile_creds = seller_profile_creds     # which part of the seller profile creation is pending
            )        
        except JWTError as error :
            raise error
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
        

class VendorOrderService :

    @staticmethod
    async def place_order(order: CreateOrderSchema, db: Session, vendor):
        try:
            # Validate vendor
            if vendor is None:
                raise HTTPException(status_code=400, detail="Error in User Details")
            
            vendor_detail = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Not Found"
                )
            
            # Validate seller exists
            seller = db.query(Seller).filter(Seller.id == order.seller_id).first()
            if not seller:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Seller Not Found"
                )
            
            # Validate factory exists
            factory = db.query(Factory).filter(Factory.id == order.factory_id).first()
            if not factory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Factory Not Found"
                )
            
            # Validate ordered products
            if not order.ordered_products or len(order.ordered_products) == 0:
                raise HTTPException(
                    status_code=400, 
                    detail="At least one product must be ordered"
                )
            
            # Extract product IDs from ordered products
            product_ids = [product.product_id for product in order.ordered_products]
            
            # Validate all products exist
            products = db.query(Product).filter(Product.id.in_(product_ids)).all()
            if len(products) != len(product_ids):
                existing_product_ids = [p.id for p in products]
                missing_product_ids = [pid for pid in product_ids if pid not in existing_product_ids]
                raise HTTPException(
                    status_code=400, 
                    detail=f"Products with IDs {missing_product_ids} not found"
                )
            
            # Validate quantities are positive
            for product_detail in order.ordered_products:
                if product_detail.quantity <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Quantity must be positive for product ID {product_detail.product_id}"
                    )
                if product_detail.total_price <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Total price must be positive for product ID {product_detail.product_id}"
                    )
            
            # Calculate and validate total amounts
            calculated_product_amount = sum([product.total_price for product in order.ordered_products])
            calculated_total = calculated_product_amount + order.platform_fee
            
            # # Optional: Validate if provided amounts match calculated amounts
            # if abs(order.product_ammount - calculated_product_amount) > 0.01:  # Allow small floating point differences
            #     raise HTTPException(
            #         status_code=400,
            #         detail=f"Product amount mismatch. Expected: {calculated_product_amount}, Provided: {order.product_ammount}"
            #     )
            
            # Create the main order
            db_order = PlaceOrder(
                vendor_id=vendor_detail.id,
                seller_id=order.seller_id,
                factory_id=order.factory_id,
                product_ammount=order.product_ammount,
                platform_fee=order.platform_fee,
                total_amount=calculated_total,
                remarks=order.remarks
            )
            
            db.add(db_order)
            db.flush()  # Flush to get the order ID without committing
            
            # Create ordered product details
            ordered_product_records = []
            for product_detail in order.ordered_products:
                db_product_detail = OrderedProductsDetail(
                    product=product_detail.product_id,
                    quantity=product_detail.quantity,
                    total_price=product_detail.total_price,
                    order_id=db_order.id
                )
                ordered_product_records.append(db_product_detail)
                db.add(db_product_detail)
            
            # Commit all changes
            db.commit()
            db.refresh(db_order)
            
            # Return the complete order with products using the response schema
            return db_order
            
        except SQLAlchemyError as db_error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(db_error)}"
            )
        except HTTPException as error:
            db.rollback()
            raise error
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )
    @staticmethod
    async def get_vendor_orders(
        db: Session, 
        vendor, 
        order_status: Optional[OrderStatusEnum] = None
    ):
        try:
            # Validate vendor
            if vendor is None:
                raise HTTPException(status_code=400, detail="Error in User Details")
            
            vendor_detail = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Not Found"
                )
            
            # Build query for vendor's orders
            query = db.query(PlaceOrder).filter(PlaceOrder.vendor_id == vendor_detail.id)
            
            # Apply status filter if provided
            if order_status:
                query = query.filter(PlaceOrder.order_status == order_status)
            
            # Apply ordering (most recent first)
            query = query.order_by(PlaceOrder.created_at.desc())
            
            # Apply pagination
            orders = query.all()
            
            # Convert to response schema
            
            print(orders)
            return orders
            
        except HTTPException as error:
            raise error
        except SQLAlchemyError as db_error:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(db_error)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )
