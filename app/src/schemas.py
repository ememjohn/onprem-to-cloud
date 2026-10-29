from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr

class OrderBase(BaseModel):
    customer_id: int
    total_amount: Decimal
    status: str = "PENDING"

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CustomerBase(BaseModel):
    name: str
    email: EmailStr

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    orders: List[OrderResponse] = []
    model_config = ConfigDict(from_attributes=True)
