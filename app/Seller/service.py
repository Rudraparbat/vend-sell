from cmath import acos, cos, sin
from datetime import date, timedelta
import json
from math import radians
import random

from sqlalchemy import case, func, select, text
from app.Seller.models import *
from app.Seller.schema import *
from app.Seller.schema import SellerFactoryDetailResponse  # Add this import if the class is defined in schema.py
from sqlalchemy.orm import Session, joinedload, selectinload
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
    async def get_states() :
        try :
            with open("static/city.json" , 'r') as file :
                json_struct = file.read()

            state_dict = json.loads(json_struct)

            return StateResponseSchema(states = list(state_dict.keys()))

        except HTTPException as httperror :
            raise httperror
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))
        
    @staticmethod
    async def get_cities_by_state(state) :
        try :
            with open("static/city.json" , 'r') as file :
                json_struct = file.read()

            state_dict = json.loads(json_struct)

            if state:
                cities = state_dict.get(state, [])
            else:
                # Flatten all cities from all states into a single list
                cities = []
                for city_list in state_dict.values():
                    if isinstance(city_list, list):
                        cities.extend(city_list)

            return CityResponseSchema(cities=cities)

        except HTTPException as httperror :
            raise httperror
        except Exception as e :
            raise HTTPException(status_code= 500 , detail= str(e))


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
    async def get_seller_factory_details(db: Session , factory_id : int) :
        try :
            query = (
                select(Factory)
                .options(
                    joinedload(Factory.seller).joinedload(Seller.vendor),
            # Location is one-to-one, so joinedload is perfect
                    joinedload(Factory.location),
                )
                .where(Factory.id == factory_id)
            )
            
            factory = db.execute(query).unique().scalar_one_or_none()
            
            if not factory:
                raise HTTPException(status_code=400 ,detail="Factory With This Id Doesnt Exist")
            
            # Filter products to only include those from this specific factory
            products_query = (
                select(Product)
                .where(Product.factory_id == factory_id)
            )
            
            factory_products = db.execute(products_query).scalars().all()
            
            # Construct response
            feature_seller = FeatureSeller(
                id=factory.seller.id,
                email=factory.seller.email,
                phone=factory.seller.phone,
                vendor=factory.seller.vendor
            )
            
            feature_factory = FeatureFactory(
                id=factory.id,
                location=[factory.location] if factory.location else [],
                products=factory_products
            )
            
            return SellerFactoryDetailResponse(
                seller=feature_seller,
                factory=feature_factory
            )

        except HTTPException as http_error :
            raise http_error
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    @staticmethod
    async def get_nearby_sellers(db : Session , loc : LocationSchema ) :
        try :

            min_radius_meters = loc.min_distance_km * 1_000
            max_radius_meters = loc.max_distance_km * 1_000

            location_filters = ["l.location IS NOT NULL"]

            if loc.city:
                location_filters.append("LOWER(l.city) = LOWER(:city)")
            
            # Distance filter using ST_DWithin for efficient spatial index usage
            location_filters.append("""
                ST_DWithin(
                    l.location::geography,
                    ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
                    :max_radius_meters
                )
            """)

            location_where = " AND ".join(location_filters)
            expanded_limit = min(200, max(50, (loc.max_distance_km // 10) * 20))
            # KNN Algorithmic query to find nearby sellers , within logn time
            query = text(f"""
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
                    ) / 1000 AS distance_km
                FROM locations l
                WHERE {location_where}
                ORDER BY l.location <-> ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
                LIMIT :expanded_limit
            ),
            filtered_with_distance AS (
                SELECT *
                FROM filtered_locations
                WHERE distance_km BETWEEN :min_distance_km AND :max_distance_km
            ),
            seller_results AS (
                SELECT DISTINCT ON (s.id)
                    s.id AS seller_id,
                    s.email AS seller_name,
                    f.id AS factory_id,
                    f.name AS factory_name,
                    f.factory_type AS factory_types,
                    f.shop_categories AS category,
                    fl.latitude AS factory_latitude,
                    fl.longitude AS factory_longitude,
                    fl.address_line1,
                    fl.city,
                    fl.state,
                    fl.country,
                    fl.distance_km
                FROM filtered_with_distance fl
                JOIN factories f ON fl.factory_id = f.id
                JOIN sellers s ON f.seller_id = s.id
                ORDER BY s.id, fl.distance_km
            )
            SELECT * FROM seller_results
            ORDER BY distance_km
            LIMIT :final_limit
        """)
            params = {
            "latitude": loc.latitude,
            "longitude": loc.longtitude,  # Note: consider renaming to longitude
            "min_distance_km": loc.min_distance_km,
            "max_distance_km": loc.max_distance_km,
            "max_radius_meters": max_radius_meters,
            "expanded_limit": expanded_limit,
            "final_limit": 20
        }
            if loc.city:
                params["city"] = loc.city

            result = db.execute(query, params)
            
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
                    factory_type = row.factory_types,
                    shop_categories = row.category ,
                    distance=row.distance_km,
                    factory_location=factory_location
                )
                
                validated_results.append(seller_response)
        
            return validated_results
            
        except SQLAlchemyError as db_error:
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    # update seller profile
    @staticmethod
    async def update_seller_profile(db : Session , update_data : SellerProfileUpdateSchmea) : 
        try :

            if update_data.seller :
                # update seller profile 
                seller = db.query(Seller).filter(Seller.id == update_data.seller.id).first()
                if not seller:
                    raise HTTPException(status_code=400, detail="Seller Details not found")
                clean_data = update_data.seller.dict(exclude_unset=True, exclude={"id"})
                for key, value in clean_data.items():
                    setattr(seller, key, value)
                

            if update_data.factories :
                # update factory details 
                factory = db.query(Factory).filter(Factory.id == update_data.factories.id).first()
                if not factory :
                    raise HTTPException(status_code=400, detail="Factory Details not found")
                
                clean_data = update_data.factories.dict(exclude_unset=True, exclude={"id"})

                for key, value in clean_data.items():
                    setattr(factory, key, value)
                
    
            if update_data.location :
                # update location details 
                location = db.query(Location).filter(Location.id == update_data.location.id).first()
                if not location :
                    raise HTTPException(status_code=400, detail="Location Details not found")
                

                clean_data = update_data.location.dict(exclude_unset=True, exclude={"id"})

                for key, value in clean_data.items():
                    setattr(location , key, value)

            if update_data.products :
                # update product details 
                products_dict_list = [product.dict(exclude_unset=True) for product in update_data.products]
                db.bulk_update_mappings(Product, products_dict_list)

            db.commit()

            return {"message" : "Seller Profile Updated Successfully"}
        except SQLAlchemyError as db_error:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(db_error))
        except Exception as e:
            db.rollback()
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
        
