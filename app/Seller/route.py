from fastapi import APIRouter, Depends, HTTPException, status , Response , Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.Seller.schema import LocationSchema, NearbySellerResponseSchema, SellerCreate, SellerFactoryDetailResponse, SellerProfileSchema, SellerProfileUpdateSchmea, SellerResponse, FactoryCreate, FactoryResponse, LocationCreate, LocationResponse, ProductBase, ProductResponse, SellerSearchSchemaResponse, StateResponseSchema, Token
from app.Seller.service import  SellerOrderService, SellerService
from typing import List, Optional
from app.Utils.database import get_db  
from app.Utils.authservice import get_current_user
seller_router = APIRouter()

@seller_router.post("/create/"  , status_code= 200 , response_model=SellerResponse)
async def create_seller(seller: SellerCreate , db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
    return await SellerService.create_seller(db , seller , vendor)


@seller_router.post("/factories/", response_model=FactoryResponse)
async def create_factory(factory: FactoryCreate, db: Session = Depends(get_db), vendor = Depends(get_current_user)):
    
    return await SellerService.create_factory(db, factory)

@seller_router.post("/factories/locations/", response_model=LocationResponse)
async def create_location(location: LocationCreate, db: Session = Depends(get_db) , vendor = Depends(get_current_user)):

    return await SellerService.create_location(db, location)

@seller_router.post("/products/create/")
async def create_product(product: List[ProductBase], db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
    
    return await SellerService.create_product(db, product)

@seller_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    return await SellerService.get_product_by_id(db, product_id)

@seller_router.get("/products/", response_model=List[ProductResponse])
async def get_products(factory_id : int ,seller_id : Optional[int] = None , db: Session = Depends(get_db)):
    return await SellerService.get_product_list(db , factory_id , seller_id)

@seller_router.get("/products-list/", response_model=List[ProductResponse])
async def get_products_for_seller(db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
    if not vendor :
        raise HTTPException(status_code=400 , detail= "vendor Detail Not Found")
    return await SellerService.get_product_list_for_seller(db , vendor)

@seller_router.get("/profile/", response_model= SellerProfileSchema)
async def seller_profile(db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
    if not vendor :
        raise HTTPException(status_code=400 , detail= "Seller Detail Not Found")
    return await SellerService.get_seller_profile(db , vendor)


@seller_router.get("/seller-detail/{factory_id}")
async def seller_detail_search(factory_id : int , db: Session = Depends(get_db)):
    return await SellerService.get_seller_factory_details(db , factory_id)

# seller search api 
@seller_router.post("/search/", status_code=200 , response_model=List[NearbySellerResponseSchema])
async def seller_search_by_loc(loc : LocationSchema , db: Session = Depends(get_db)):
   
    return await SellerService.get_nearby_sellers(db , loc)

# Seller Detail Update Api 
@seller_router.put("/edit/profile/", status_code=200 , response_model=dict)
async def update_seller_profile(update_data : SellerProfileUpdateSchmea  , db: Session = Depends(get_db)) :
    return await SellerService.update_seller_profile(db , update_data)


@seller_router.post("/placed-orders/", status_code=200)
async def placed_order_for_seller(db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
   
    return await SellerOrderService.my_orders(db , vendor) 

# State List APi
@seller_router.get("/states/", status_code=200)
async def get_states_list():
    return await SellerService.get_states() 

# city list Api 
@seller_router.get("/cities/", status_code=200)
async def get_cities_list(state : Optional[str] = None):
    return await SellerService.get_cities_by_state(state) 