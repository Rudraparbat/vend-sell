from enum import Enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.Utils.database import Base
from datetime import datetime

class Vendoruser(Base):
    __tablename__ = "vendoruser"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shops = relationship("VendorShopDetail", back_populates="vendor", cascade="all, delete-orphan")
    locations = relationship("VendorShopLocation", back_populates="vendor", cascade="all, delete-orphan")

class VendorShopDetail(Base):
    __tablename__ = "vendorshop"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendoruser.id"), nullable=False)
    shop_name = Column(String, nullable=False)
    contact_number = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendoruser", back_populates="shops")
    locations = relationship("VendorShopLocation", back_populates="shop", cascade="all, delete-orphan")

class VendorShopLocation(Base):
    __tablename__ = "vendor_location"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("vendorshop.id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendoruser.id"), nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    vendor = relationship("Vendoruser", back_populates="locations")
    shop = relationship("VendorShopDetail", back_populates="locations")