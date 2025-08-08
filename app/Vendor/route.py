from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.Utils.authservice import get_current_user
from app.Utils.database import get_db
from app.Vendor.schema import *
from app.Vendor.service import VendorAuthService, VendorOrderService, VendorService

vendor_router = APIRouter()


@vendor_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_vendor(response : Response , vendor: VendorUserCreate, db: Session = Depends(get_db)):
    return await VendorService.create_vendor_user(db, vendor , response)

@vendor_router.post("/location/create", status_code=status.HTTP_201_CREATED)
async def create_location(location: VendorLocationCreate, db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
    return await VendorService.create_vendor_location(db, location , vendor)

@vendor_router.post("/shop/create", status_code=status.HTTP_201_CREATED)
async def create_shop(shop: VendorShopCreate, db: Session = Depends(get_db) ,  vendor = Depends(get_current_user)):
    return await VendorService.save_vendor_shop_details(db, shop , vendor)

@vendor_router.get("/profile/", response_model=VendorUserResponse)
async def get_profile(db: Session = Depends(get_db) , vendor = Depends(get_current_user)):
    return await VendorService.vendor_profile(db, vendor)

@vendor_router.post("/login", status_code=status.HTTP_200_OK)
async def login_vendor(response : Response , form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await VendorAuthService.authenticate_user(db, form_data.username, form_data.password , response)

@vendor_router.post("/oauth/login", status_code=status.HTTP_200_OK)
async def login_vendor(request  : Request , response : Response):
    return await VendorAuthService.google_auth_service(request , response)

@vendor_router.post("/logout/")
async def get_profile(response : Response):
    return await VendorAuthService.logout(response)

@vendor_router.get("/vendor-status/")
async def get_vendor_status(request : Request , db: Session = Depends(get_db)):
    return await VendorAuthService.vendor_status(db , request)

@vendor_router.post("/placeorder/")
async def place_order(order: CreateOrderSchema,  db: Session = Depends(get_db),  vendor = Depends(get_current_user)):
    return await VendorOrderService.place_order(order, db, vendor)

@vendor_router.get("/orders/", response_model=List[PlaceOrderSchema])
async def get_my_orders(
    db: Session = Depends(get_db),
    vendor = Depends(get_current_user),
    order_status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status")
):
    return await VendorOrderService.get_vendor_orders(db, vendor, order_status)
