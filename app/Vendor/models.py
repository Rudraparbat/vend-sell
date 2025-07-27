from enum import Enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table , Enum as SqlEnum
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

class OrderStatusEnum(str, Enum):
    PLACED = "placed"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str , Enum) :
    COD = "cod"
    GPAY = "gpay"

class PlaceOrder(Base):
    __tablename__ = "placeorder"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendoruser.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    
    order_status = Column(SqlEnum(OrderStatusEnum), default=OrderStatusEnum.PLACED)
    payment_method = Column(SqlEnum(PaymentMethod), default=PaymentMethod.COD)
    order_otp = Column(String(6), nullable=True)
    product_ammount = Column(Float, nullable=False)
    platform_fee = Column(Float, default=10)
    
    total_amount = Column(Float, default=0.0)
    remarks = Column(String(255), nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vendor = relationship("Vendoruser")
    seller = relationship("Seller")
    factory = relationship("Factory")
    
    # Many-to-many relationship with OrderedProductsDetail
    ordered_products = relationship("OrderedProductsDetail", back_populates="order")


class OrderedProductsDetail(Base):
    __tablename__ = "product_detail"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer)
    total_price = Column(Float, nullable=False)
    
    # Foreign key to link with PlaceOrder
    order_id = Column(Integer, ForeignKey("placeorder.id"), nullable=False)
    
    # Back reference to PlaceOrder
    order = relationship("PlaceOrder", back_populates="ordered_products")
