from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import BaseModel
import os

load_dotenv()
DB_URI = os.getenv("DB_URI")

app = FastAPI()
print(DB_URI)

client = MongoClient(DB_URI)
db = client["restaurants"]


# Display the message on the webbrowser
@app.get("/orders")
async def get_orders():
    orders = list(db.orders.find({}))
    for order in orders:
        order["_id"] = str(order["_id"])  # Convert ObjectId to string
    return orders


# Find a single document
@app.get("/orders/{orderNum}")
async def get_order_by_order_num(orderNum: int): 
    order = db.orders.find_one({"orderNum": orderNum})
    if order:
        order["_id"] = str(order["_id"])
        return order
    else:
        return {"detail": "Order not found"}

# Delete a single document
@app.delete("/orders/{orderNum}")
async def delete_order_by_order_num(orderNum: int):
    db.orders.delete_one({"orderNum": orderNum})
    return {"message": "{orderNum} successfully deleted!"}

# Update a document
query_update = { "orderNum": 35 }
update_values = { "$set": { "isDelivered": False } }

@app.put("/orders/{orderNum}")
async def update_order(orderNum: int):
    db.orders.update_one(query_update, update_values)
    return {"message": "{orderNum} successfully updated!"}

# Insert a new document
class Order(BaseModel):
    orderNum: int
    customerName: str
    customerPhone: str
    customerEmail: str
    orderedMenu: list[str]
    isDelivered: bool
    orderTotal: float

@app.post("/orders")
async def insert_order(order: Order):
    query_insert = order.model_dump()
    db.orders.insert_one(query_insert)
    return {"message": "Data successfully inserted!"}
