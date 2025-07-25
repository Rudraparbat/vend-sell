from enum import Enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime , Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.Utils.database import Base
from datetime import datetime


class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    factories = relationship("Factory", back_populates="seller")
    products = relationship("Product", back_populates="seller")

class FactoryTypeEnum(str , Enum) :
    FACTORY = "factory"
    SHOP = "shop"
    WAREHOUSE = "warehouse"


class Factory(Base):
    __tablename__ = "factories"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    name = Column(String, nullable=False)
    factory_type = Column(SqlEnum(FactoryTypeEnum), nullable=False)  # e.g., 'factory', 'shop', 'warehouse'
    contact_number = Column(String(10) , nullable=False)
    
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
