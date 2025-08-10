from enum import Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Column, Integer, String, Float, ForeignKey, DateTime , Enum as SqlEnum, Text
from sqlalchemy.orm import relationship
from app.Utils.database import Base
from datetime import datetime
from geoalchemy2 import Geometry



class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer , ForeignKey('vendoruser.id') , nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    factories = relationship("Factory", back_populates="seller")
    products = relationship("Product", back_populates="seller")
    vendor = relationship("Vendoruser")

    ratings = relationship("Rating", back_populates="seller")  
    
    # Helper properties for rating calculations
    @property
    def average_rating(self):
        """Calculate average rating"""
        if not self.ratings:
            return 0.0
        return sum(rating.rating.value for rating in self.ratings) / len(self.ratings)
    
    @property
    def total_ratings(self):
        """Get total number of ratings"""
        return len(self.ratings)
    
    @property
    def rating_distribution(self):
        """Get distribution of ratings (1-5 stars)"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in self.ratings:
            distribution[rating.rating.value] += 1
        return distribution

class FactoryTypeEnum(str , Enum) :
    FACTORY = "factory"
    SHOP = "shop"
    WAREHOUSE = "warehouse"

class ShopCategoryEnum(str, Enum):
    ELECTRONICS = "electronics"
    GROCERY = "grocery"
    CLOTHING = "clothing"
    PHARMACY = "pharmacy"
    TOYS = "toys"
    FURNITURE = "furniture"
    SPORTS = "sports"
    BOOKS = "books"
    BEAUTY = "beauty"
    AUTOMOTIVE = "automotive"

class Factory(Base):
    __tablename__ = "factories"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    name = Column(String, nullable=False)
    factory_type = Column(SqlEnum(FactoryTypeEnum), nullable=False)  # e.g., 'factory', 'shop', 'warehouse'
    contact_number = Column(String(10) , nullable=False)
    # shop_categories = Column(JSONB, nullable=False, default=[])
    # Relationships
    seller = relationship("Seller", back_populates="factories")
    location = relationship("Location", back_populates="factory", uselist=False)

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Add geometry column for spatial indexing
    location = Column(Geometry('POINT', srid=4326))
    # Relationship
    factory = relationship("Factory", back_populates="location")

class QuantifiableTypeEnum(str, Enum):
    UNIT = "unit"
    KILOGRAM = "kilogram"
    GRAM = "gram"
    LITER = "liter"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    qunatity_unit = Column(SqlEnum(QuantifiableTypeEnum), nullable=False)  # e.g., 'unit', 'kilogram', 'gram', 'liter'
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    seller = relationship("Seller", back_populates="products")

class RatingEnum(int, Enum):
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey('vendoruser.id'), nullable=False)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=False)
    # order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)  # Optional: link to specific order
    
    rating = Column(SqlEnum(RatingEnum), nullable=False)  # 1-5 stars
    review_text = Column(Text , nullable = True)  # Optional detailed review

    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendoruser")  # Who gave the rating
    seller = relationship("Seller", back_populates="ratings")
    # order = relationship("Order")  # Uncomment when you have Order model