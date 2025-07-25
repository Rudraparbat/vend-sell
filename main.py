from fastapi import FastAPI , Depends
from app.Utils.database import engine, Base
import os
from app.Seller.route import seller_router


app = FastAPI()
@app.get("/")
def read_root():
    return {"Message": "Welcome to the Vendor seller application!"}


Base.metadata.create_all(bind=engine)

# os.makedirs(os.getenv("UPLOAD_DIR"), exist_ok=True)


app.include_router(
    seller_router,
    prefix="/seller",
    tags=["Seller Management"]
)