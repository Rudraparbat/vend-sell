from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.Utils.database import get_db
import bcrypt

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

    class Config :
        from_attributes = True



