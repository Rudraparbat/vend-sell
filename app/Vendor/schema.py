from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.Utils.database import get_db
import bcrypt

from app.Vendor.models import OrderStatusEnum, PaymentMethod

class VendorUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: constr(pattern=r'^\d{10}$') # type: ignore

class VendoruserCreateResponse(BaseModel) :
    name: str
    loginid : EmailStr
    password: str

    class Config :
        from_attributes = True


    
class VendorShopCreate(BaseModel):
    shop_name: str
    contact_number: constr(pattern=r'^\d{10}$') # type: ignore

class VendorLocationCreate(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class VendorShopLocationResponse(BaseModel):
    id: int
    shop_id: Optional[int]
    vendor_id: int
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    country: str
    postal_code: str
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True

class VendorShopResponse(BaseModel):
    id: int
    vendor_id: int
    shop_name: str
    contact_number: str
    created_at: datetime
    locations: List[VendorShopLocationResponse]

    class Config:
        from_attributes = True

class VendorUserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime
    shops: List[VendorShopResponse]
    locations: List[VendorShopLocationResponse]

    class Config:
        from_attributes = True

class VendorStatusSChema(BaseModel) :
    is_login : bool
    is_seller : bool

    class Config :
        from_attributes = True

class OrderedProductSchema(BaseModel):

    product: int
    quantity: int
    total_price: float
    
    class Config:
        from_attributes = True

class OrderdProductResponse(OrderedProductSchema) :
    id : int

    class Config:
        from_attributes = True



class PlaceOrderSchema(BaseModel):
    id: Optional[int] = None
    vendor_id: int
    seller_id: int
    factory_id: int
    
    order_status: OrderStatusEnum = OrderStatusEnum.PLACED
    payment_method: PaymentMethod = PaymentMethod.COD
    order_otp: Optional[str] = None
    product_ammount: float
    platform_fee: float = 10.0
    
    total_amount: float = 0.0
    remarks: Optional[str] = None
    delivery_date: Optional[datetime] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # List of ordered products
    ordered_products: List[OrderedProductSchema] = []
    
    class Config:
        from_attributes = True

class CreateOrderSchema(BaseModel):
    seller_id: int
    factory_id: int
    product_ammount : float 
    platform_fee: float = 10.0
    total_amount: float 
    remarks: Optional[str] = None

    
    # Products to be ordered
    ordered_products: List[OrderedProductSchema]


class OrderResponseSchema(PlaceOrderSchema):
    # You can add computed fields here
    total_items: Optional[int] = None
    
    class Config:
        from_attributes = True
        
    @property
    def total_items_count(self) -> int:
        return len(self.ordered_products)