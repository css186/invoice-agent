from pydantic import BaseModel, field_validator
from typing import List, Optional, Union
from datetime import date

class Item(BaseModel):
    original_input: str
    item_name: str
    quantity: Optional[Union[str, int, float]] = None
    unit: Optional[str] = None

    @field_validator("quantity", mode="before")
    def quantity_to_str(cls, v):
        return str(v) if v is not None else None

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