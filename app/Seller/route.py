from fastapi import APIRouter, Depends, HTTPException, status , Response , Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.Seller.schema import SellerCreate, SellerProfileSchema, SellerResponse, FactoryCreate, FactoryResponse, LocationCreate, LocationResponse, ProductBase, ProductResponse, Token
from app.Seller.service import SellerAuthService, SellerService
from typing import List, Optional
from app.Utils.database import get_db  
from app.Utils.authservice import get_current_user
seller_router = APIRouter()

@seller_router.post("/create/"  , status_code= 200)
async def create_seller(seller: SellerCreate , db: Session = Depends(get_db)):
    return await SellerService.create_seller(db , seller)

@seller_router.post("/login", response_model=Token)
async def login_for_access_token(response : Response , form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    return await SellerAuthService.authenticate_user(db, form_data.username, form_data.password , response)

@seller_router.post("/factories/", response_model=FactoryResponse)
async def create_factory(factory: FactoryCreate, db: Session = Depends(get_db)):
    
    return await SellerService.create_factory(db, factory)

@seller_router.post("/factories/locations/", response_model=LocationResponse)
async def create_location(location: LocationCreate, db: Session = Depends(get_db)):

    return await SellerService.create_location(db, location)

@seller_router.post("/products/create/", response_model=ProductResponse)
async def create_product(product: ProductBase, db: Session = Depends(get_db)):
    
    return await SellerService.create_product(db, product)

@seller_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db) , seller = Depends(get_current_user)):
    if not seller :
        print("seller is" , seller)
        raise HTTPException(status_code= 400 , detail= "Please Login First")
    print(seller)
    return await SellerService.get_product_by_id(db, product_id)

@seller_router.get("/products/", response_model=List[ProductResponse])
async def get_products(factory_id : int ,seller_id : Optional[int] = None , db: Session = Depends(get_db)):
    return await SellerService.get_product_list(db , factory_id , seller_id)

@seller_router.get("/products-list/", response_model=List[ProductResponse])
async def get_products_for_seller(db: Session = Depends(get_db) , seller = Depends(get_current_user)):
    if not seller :
        raise HTTPException(status_code=400 , detail= "Seller Detail Not Found")
    return await SellerService.get_product_list_for_seller(db , seller)

@seller_router.get("/profile/", response_model= SellerProfileSchema)
async def seller_profile(db: Session = Depends(get_db) , seller = Depends(get_current_user)):
    if not seller :
        raise HTTPException(status_code=400 , detail= "Seller Detail Not Found")
    return await SellerService.get_seller_profile(db , seller)
