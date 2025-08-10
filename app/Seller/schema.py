from enum import Enum
from typing import Optional, List
from datetime import datetime
from app.Seller.models import FactoryTypeEnum , QuantifiableTypeEnum , ShopCategoryEnum
from pydantic import BaseModel, EmailStr, Field, validator



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
    # shop_categories : List[ShopCategoryEnum]

class FactoryCreate(FactoryBase):
    pass

class FactoryResponse(FactoryBase):
    id: int
    location: Optional[LocationResponse] = []
    
    class Config:
        from_attributes = True

class SellerBase(BaseModel):
    email: EmailStr
    phone: str

class SellerCreate(SellerBase):
    pass

class SellerResponse(SellerBase):
    id: int
    vendor_id : int
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

class VendorDetailSchema(BaseModel) :
    id : int
    name : str
    email : EmailStr
    phone : str

    class Config :
        from_attributes = True

class SellerProfileSchema(BaseModel) :
    id : int
    email : EmailStr
    phone : str
    factories : Optional[List[FactoryResponse]] = []
    products : Optional[List[ProductResponse]] = []
    vendor : VendorDetailSchema

    class Config :
        from_attributes = True

class FeatureSeller(BaseModel) :
    id : int
    email : EmailStr
    phone : str
    vendor : VendorDetailSchema

    class Config :
        from_attributes = True

class FeatureFactory(BaseModel) :
    id: int
    location: Optional[List[LocationResponse]] = []
    products : Optional[List[ProductResponse]] = []

    class Config :
        from_attributes = True



class SellerFactoryDetailResponse(BaseModel) :
    seller : FeatureSeller
    factory : FeatureFactory

    class Config :
        from_attributes = True

    

class LocationSchema(BaseModel) :
    latitude : float
    longtitude : float


class SellerSearchSchemaResponse(BaseModel) :
    seller : SellerProfileSchema
    distance : float

    class Config :
        from_attributes = True

class FactoryLocationSchema(BaseModel):
    """Schema for factory location details"""
    latitude: float
    longitude: float
    address_line1: str
    city: str
    state: str
    country: str
    full_address: str

    class Config:
        from_attributes = True

class NearbySellerResponseSchema(BaseModel):
    """Schema for nearby seller response with factory location"""
    seller_id: int
    seller_name: str
    factory_id: int
    factory_name: str
    factory_type : str
    distance: float
    factory_location: FactoryLocationSchema

    class Config:
        from_attributes = True

# For the complete response (list of sellers)
from typing import List

class NearbySellerListResponseSchema(BaseModel):
    """Schema for list of nearby sellers"""
    sellers: List[NearbySellerResponseSchema]
    total_count: int
    
    class Config:
        from_attributes = True

# Enum for rating values (matching your SQLAlchemy enum)
class RatingValue(int, Enum):
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5

# Schema for creating a new rating
class RatingCreate(BaseModel):
    seller_id: int = Field(..., description="ID of the seller being rated")
    order_id: Optional[int] = Field(None, description="Optional order ID this rating is for")
    rating: RatingValue = Field(..., description="Rating value from 1-5 stars")
    review_text: Optional[str] = Field(None, max_length=1000, description="Optional review text")
    
    @validator('review_text')
    def validate_review_text(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

# Schema for updating a rating
class RatingUpdate(BaseModel):
    rating: Optional[RatingValue] = Field(None, description="Updated rating value")
    review_text: Optional[str] = Field(None, max_length=1000, description="Updated review text")
    
    @validator('review_text')
    def validate_review_text(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

# Base schema for rating response
class RatingBase(BaseModel):
    id: int
    vendor_id: int
    seller_id: int
    order_id: Optional[int]
    rating: RatingValue
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schema for detailed rating response (includes related data)
class RatingResponse(RatingBase):
    # You can add related vendor/seller info if needed
    pass

# Schema for rating response with vendor info
class RatingWithVendorResponse(RatingBase):
    vendor_email: Optional[str] = None  # If you want to show who gave the rating
    
    class Config:
        from_attributes = True

# Schema for rating response with seller info
class RatingWithSellerResponse(RatingBase):
    seller_email: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema for rating statistics (useful for seller profiles)
class RatingStats(BaseModel):
    average_rating: float = Field(0.0, description="Average rating score")
    total_ratings: int = Field(0, description="Total number of ratings")
    rating_distribution: dict = Field(default_factory=dict, description="Distribution of ratings (1-5)")
    
    class Config:
        from_attributes = True

# Schema for listing ratings with pagination info
class RatingListResponse(BaseModel):
    ratings: list[RatingResponse]
    total: int
    page: int
    size: int
    pages: int

# Schema for rating summary (useful for seller cards/listings)
class RatingSummary(BaseModel):
    seller_id: int
    average_rating: float
    total_ratings: int
    latest_review: Optional[str] = None
    latest_rating_date: Optional[datetime] = None
