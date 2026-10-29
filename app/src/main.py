import logging
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.config import settings
from src.database import get_db
from src.models import Customer, Order
from src.schemas import CustomerResponse, OrderResponse, OrderCreate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("oms-core")

app = FastAPI(title=settings.app_name, version="1.0.0")

@app.get("/healthz", tags=["Ops"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.app_env
        }
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable"
        )

@app.get("/api/v1/customers", response_model=list[CustomerResponse], tags=["Customers"])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).order_by(Customer.id).all()

@app.get("/api/v1/orders", response_model=list[OrderResponse], tags=["Orders"])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id).all()

@app.post("/api/v1/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    order = Order(
        customer_id=payload.customer_id,
        total_amount=payload.total_amount,
        status=payload.status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
