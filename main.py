from fastapi import FastAPI , Depends
from app.Utils.database import engine, Base
import os
from fastapi.middleware.cors import CORSMiddleware
from app.Seller.route import seller_router


app = FastAPI()
@app.get("/")
def read_root():
    return {"Message": "Welcome to the Vendor seller application!"}


Base.metadata.create_all(bind=engine)

# os.makedirs(os.getenv("UPLOAD_DIR"), exist_ok=True)
allow_origin = [
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
# include middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    seller_router,
    prefix="/seller",
    tags=["Seller Management"]
)