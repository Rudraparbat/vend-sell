from typing import Optional, List
from datetime import datetime
from app.Seller.models import FactoryTypeEnum , QuantifiableTypeEnum
from pydantic import BaseModel, EmailStr



class LocationBase(BaseModel):
    factory_id : int
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    factory_id: int
    
    class Config:
        from_attributes = True

class FactoryBase(BaseModel):
    seller_id : int
    name: str
    factory_type: FactoryTypeEnum
    contact_number: Optional[str] = None

class FactoryCreate(FactoryBase):
    pass

class FactoryResponse(FactoryBase):
    id: int
    location: Optional[LocationResponse] = []
    
    class Config:
        from_attributes = True

class SellerBase(BaseModel):
    name: str
    email: EmailStr
    hashed_password : str
    phone: str

class SellerCreate(SellerBase):
    pass

class SellerResponse(BaseModel):
    id: int
    loginid : EmailStr
    password : str
    created_at: datetime
    factories: List[FactoryResponse] = []
    products: List["ProductResponse"] = []
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    seller_id : int
    factory_id : int
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    qunatity_unit : QuantifiableTypeEnum
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel) :
    email : EmailStr
    name : str

    class Config :
        from_attributes = True


class SellerProfileSchema(BaseModel) :
    id : int
    name : str
    email : EmailStr
    phone : str
    factories : Optional[List[FactoryResponse]] = []
    products : Optional[List[ProductResponse]] = []

    class Config :
        from_attributes = True

    

