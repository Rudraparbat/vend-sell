from cmath import acos, cos, sin
from datetime import date, timedelta
from math import radians
import random

from sqlalchemy import case, func, text
from app.Seller.models import *
from app.Seller.schema import *
from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from math import radians, cos, sin, acos
from geopy.geocoders import Nominatim
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from app.Utils.generate_invoice import generate_invoice_pdf
from app.Vendor.models import OrderStatusEnum, PlaceOrder, Vendoruser
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
    async def create_seller(db: Session, seller: SellerCreate , vendor):
        try :
            db_user = db.query(Seller).filter(Seller.email == seller.email).first()
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Not Found"
                )
            
            seller_dict = seller.dict()
            seller_dict["vendor_id"] = vendor_detail.id

            db_seller = Seller(**seller_dict)
            db.add(db_seller)
            db.commit()
            db.refresh(db_seller)

            return db_seller
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
    async def create_product(db: Session, product: List[ProductBase]):
        try :
            product_dicts = [products.dict() for products in product]

            db.bulk_insert_mappings(Product, product_dicts)
            db.commit()
            return {"status": "success", "inserted": len(product_dicts)}
        
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
    async def get_product_list_for_seller( db: Session , vendor : TokenData):
        try :
            vendor_data = db.query(Vendoruser).filter(Seller.email == vendor.email).first()
            if not vendor_data :
                raise HTTPException(status_code= 400 , detail="Seller Data Not Found")
            
            seller_data = db.query(Seller).filter(Seller.vendor_id == vendor_data.id).first()
            return seller_data.products
        
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def get_seller_profile(db: Session , vendor : TokenData) :
        try :
            vendor_data = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_data :
                raise HTTPException(status_code= 400 , detail="Seller Data Not Found")
            
            seller_data = db.query(Seller).filter(Seller.vendor_id == vendor_data.id).first()

            return seller_data
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    @staticmethod
    async def get_nearby_sellers(db : Session , loc : LocationSchema ) :
        try :
            
            # KNN Algorithmic query to find nearby sellers , within logn time
            query = text("""
            WITH filtered_locations AS (
                SELECT 
                    l.id,
                    l.factory_id,
                    l.latitude,
                    l.longitude,
                    l.address_line1,
                    l.city,
                    l.state,
                    l.country,
                    l.location,
                    ST_Distance(
                        l.location::geography, 
                        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography
                    ) / 1000 as distance_km
                FROM locations l
                WHERE l.location IS NOT NULL
                AND ST_DWithin(
                    l.location::geography,
                    ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
                    :radius_meters
                )
                ORDER BY l.location <-> ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
                LIMIT :expanded_limit
            ),
            seller_results AS (
                SELECT DISTINCT ON (s.id)
                    s.id as seller_id,
                    s.email as seller_name,
                    f.id as factory_id,
                    f.name as factory_name,
                    fl.latitude as factory_latitude,
                    fl.longitude as factory_longitude,
                    fl.address_line1,
                    fl.city,
                    fl.state,
                    fl.country,
                    fl.distance_km
                FROM filtered_locations fl
                JOIN factories f ON fl.factory_id = f.id
                JOIN sellers s ON f.seller_id = s.id
                ORDER BY s.id, fl.distance_km
            )
            SELECT * FROM seller_results 
            ORDER BY distance_km
            LIMIT :final_limit
        """)

            result = db.execute(query, {
                'latitude': loc.latitude,
                'longitude': loc.longtitude,
                'radius_meters': 500000,  # 500km radius
                'expanded_limit': 200,   # Get more locations initially
                'final_limit': 20        # Final seller limit
            })
            
            seller_data = result.fetchall()

            if not seller_data:
                return []

            validated_results = []
            for row in seller_data:
                # Create factory location object
                factory_location = FactoryLocationSchema(
                    latitude=row.factory_latitude,
                    longitude=row.factory_longitude,
                    address_line1=row.address_line1,
                    city=row.city,
                    state=row.state,
                    country=row.country,
                    full_address=f"{row.address_line1}, {row.city}, {row.state}, {row.country}"
                )
                
                # Create seller response object
                seller_response = NearbySellerResponseSchema(
                    seller_id=row.seller_id,
                    seller_name=row.seller_name,
                    factory_id=row.factory_id,
                    factory_name=row.factory_name,
                    distance=row.distance_km,
                    factory_location=factory_location
                )
                
                validated_results.append(seller_response)
        
            return validated_results
            
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def get_all_sellers_for_city(db : Session , loc : LocationSchema , city : str) :
        try :
            if city is None :
                city = await SellerService.get_city_from_latlon(loc.latitude , loc.longtitude)

                if not city:
                    raise HTTPException(status_code=400 , detail="Cant Locate Your City Currently")
            
            print(city)

            # Haversine expression
            distance_expr =  SellerService.haversine_sql_expr(loc.latitude, loc.longtitude).label("distance_km")

            
            query = (
                db.query(
                    Seller,
                    distance_expr
                )
                .join(Factory, Factory.seller_id == Seller.id)
                .join(Location, Location.factory_id == Factory.id)
                .filter(Location.city == city)
                .order_by(distance_expr.asc())
            )

            sellers = query.all()
            print(sellers)

            return [
                SellerSearchSchemaResponse(seller=seller, distance=distance)
                for seller, distance in sellers
            ]
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class SellerOrderService :

    @staticmethod
    async def my_orders(db : Session , vendor) :
        try :
            vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Not Found"
                )
            seller_detail = db.query(Seller).filter(Seller.vendor_id == vendor_detail.id).first()

            if not seller_detail :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Seller Detail Not Found"
                )
            
            fetch_orders = db.query(PlaceOrder).filter(
                PlaceOrder.seller_id == seller_detail.id ,
                PlaceOrder.order_status == OrderStatusEnum.PLACED
            )

            return fetch_orders.all()

        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def accept_incoming_order(order_id : int , expected_delivery : date , db : Session , vendor)  :
        try :
            vendor_detail  = db.query(Vendoruser).filter(Vendoruser.email == vendor.email).first()
            if not vendor_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vendor Not Found"
                )
            seller_detail = db.query(Seller).filter(Seller.vendor_id == vendor_detail.id).first()

            if not seller_detail :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Seller Detail Not Found"
                )
            
            order_detail = db.query(PlaceOrder).filter(PlaceOrder.id == order_id).first()

            if not order_detail :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order Detail Not Found"
                )
            
            order_detail.order_status = OrderStatusEnum.CONFIRMED
            order_detail.order_otp = random.randint(1000 , 999999)
            order_detail.delivery_date = expected_delivery

            db.commit()

            file_path = f"invoice_order_{order_id}.pdf"
            await generate_invoice_pdf(order_detail, file_path=file_path)

            return {"message": "Order confirmed and invoice generated", "invoice_path": file_path}
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    async def reject_incoming_order(order_id : int , db : Session , vendor) :
        try :
            pass

        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        