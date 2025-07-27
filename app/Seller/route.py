from fastapi import APIRouter, Depends, HTTPException, status , Response , Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.Seller.schema import LocationSchema, SellerCreate, SellerProfileSchema, SellerResponse, FactoryCreate, FactoryResponse, LocationCreate, LocationResponse, ProductBase, ProductResponse, SellerSearchSchemaResponse, Token
from app.Seller.service import  SellerService
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

# seller search api 
@seller_router.post("/search/", status_code=200)
async def seller_search_by_loc(loc : LocationSchema , db: Session = Depends(get_db)):
   
    return await SellerService.get_nearby_sellers(db , loc)

@seller_router.post("/default/search/", status_code=200)
async def seller_search_by_default(loc : LocationSchema , db: Session = Depends(get_db) ,city : Optional[str] = None):
   
    return await SellerService.get_all_sellers_for_city(db , loc , city) 