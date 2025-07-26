from fastapi import FastAPI , Depends
from app.Utils.database import engine, Base
import os
from fastapi.middleware.cors import CORSMiddleware
from app.Seller.route import seller_router
from app.Vendor.route import vendor_router


app = FastAPI()
@app.get("/")
def read_root():
    return {"Message": "Welcome to the Vendor seller application!"}


Base.metadata.create_all(bind=engine)

# os.makedirs(os.getenv("UPLOAD_DIR"), exist_ok=True)
allow_origin = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origin,   # ✅ No trailing slashes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    seller_router,
    prefix="/seller",
    tags=["Seller Management"]
)
app.include_router(
    vendor_router,
    prefix="/vendor",
    tags=["Vendor Management"]
)