from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from datetime import timedelta
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb+srv://rewearuser:rewearpass123@cluster0.v5vgvp5.mongodb.net/")
db = client["rewear"]
users_collection = db["users"]
items_collection = db["items"]

# Models
class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class Item(BaseModel):
    title: str
    description: str
    category: str
    type: str
    size: str
    condition: str
    tags: list[str] = []
    images: list[str] = []

# Token security scheme
oauth2_scheme = HTTPBearer()

# Get current user from token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    if token.startswith("Bearer "):
        token = token[7:]
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Signup
@app.post("/signup")
def signup(request: SignupRequest):
    if users_collection.find_one({"email": request.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(request.password)
    user = {
        "email": request.email,
        "password": hashed_pw,
        "name": request.name,
        "points": 0
    }
    users_collection.insert_one(user)
    return {"message": "User created successfully"}

# Login
@app.post("/login")
def login(request: LoginRequest):
    user = users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Profile (protected)
@app.get("/profile")
def read_profile(current_user: dict = Depends(get_current_user)):
    return {
        "email": current_user["email"],
        "name": current_user["name"],
        "points": current_user.get("points", 0)
    }

# Create item
@app.post("/items")
def create_item(item: Item, current_user: dict = Depends(get_current_user)):
    new_item = item.dict()
    new_item.update({
        "owner_id": str(current_user["_id"]),
        "status": "available",
        "swap_requests": []
    })
    result = items_collection.insert_one(new_item)
    return {"message": "Item created", "item_id": str(result.inserted_id)}

# List all items
@app.get("/items")
def list_items():
    items = []
    for item in items_collection.find():
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

# Get single item
@app.get("/items/{item_id}")
def get_item(item_id: str):
    item = items_collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item["_id"] = str(item["_id"])
    return item

# Update item status
@app.patch("/items/{item_id}/status")
def update_item_status(
    item_id: str,
    status: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    result = items_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Status updated", "status": status}

# Request a swap
@app.post("/items/{item_id}/request_swap")
def request_swap(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = items_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$addToSet": {"swap_requests": str(current_user["_id"])}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Swap request submitted"}

# Redeem via points
@app.post("/items/{item_id}/redeem")
def redeem_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    cost = 10
    if current_user.get("points", 0) < cost:
        raise HTTPException(status_code=400, detail="Not enough points to redeem")

    result = items_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"status": "redeemed"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$inc": {"points": -cost}}
    )

    return {"message": "Item redeemed successfully", "points_deducted": cost}

# Admin route to delete item
@app.delete("/admin/items/{item_id}")
def delete_item(item_id: str, current_user: dict = Depends(get_current_user)):
    result = items_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
