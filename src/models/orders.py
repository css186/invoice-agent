from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Item(BaseModel):
    original_input: str
    item_name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None

class Product(BaseModel):
    id: str
    product_name: str
    unit: str
    currency: str
    unit_price: float

class MatchRequest(BaseModel):
    customer_name: Optional[str] = "未知客戶"
    order_date: Optional[date] = None
    items: List[Item]
    product_list: List[Product]