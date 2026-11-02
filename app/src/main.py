import logging
from pathlib import Path
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.config import settings
from src.database import get_db
from src.models import Customer, Order
from src.schemas import CustomerResponse, OrderResponse, OrderCreate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bank-ledger-core")

app = FastAPI(title="Sabay Premium Bank", version="3.0.0")

TEMPLATE_FILE = Path(__file__).parent / "templates" / "dashboard.html"

@app.get("/", response_class=HTMLResponse, tags=["Portal"])
def banking_dashboard(db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.id).all()
    orders = db.query(Order).order_by(Order.id.desc()).all()
    
    total_volume = sum(order.total_amount for order in orders) if orders else Decimal("0.00")
    order_count = len(orders)
    avg_ticket = (total_volume / order_count) if order_count > 0 else Decimal("0.00")
    
    settled_orders = sum(1 for o in orders if o.status in ["SETTLED", "COMPLETED"])
    settlement_rate = (settled_orders / order_count * 100) if order_count > 0 else 100.0
    
    rows_html = ""
    for o in orders:
        badge_style = "bg-emerald-50 text-emerald-700 border border-emerald-200/70" if o.status in ["COMPLETED", "SETTLED"] else "bg-amber-50 text-amber-700 border border-amber-200/70"
        cust_name = o.customer.name if o.customer else f"Account #{o.customer_id}"
        date_str = o.created_at.strftime("%b %d, %Y at %H:%M UTC") if o.created_at else "Pending"
        
        rows_html += f"""
        <tr class="border-b border-slate-100 hover:bg-slate-50/80 transition-colors">
            <td class="py-3.5 px-4 font-mono text-xs text-slate-500 font-semibold">TXN-{o.id:04d}</td>
            <td class="py-3.5 px-4">
                <div class="font-medium text-slate-900 text-sm">{cust_name}</div>
                <div class="text-[11px] font-mono text-slate-400">ACCT-00{o.customer_id}</div>
            </td>
            <td class="py-3.5 px-4 font-mono font-semibold text-slate-900 text-sm">${float(o.total_amount):,.2f}</td>
            <td class="py-3.5 px-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {badge_style}">{o.status}</span>
            </td>
            <td class="py-3.5 px-4 text-xs text-slate-500 font-mono">{date_str}</td>
        </tr>
        """
        
    options_html = "".join([f"<option value='{c.id}'>{c.name} (ACCT-00{c.id})</option>" for c in customers])
    
    if not TEMPLATE_FILE.exists():
        return HTMLResponse(content="<h1>Dashboard template missing</h1>", status_code=500)
        
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    rendered = (
        template.replace("{{TOTAL_VOLUME}}", f"${float(total_volume):,.2f}")
        .replace("{{CUSTOMERS_COUNT}}", str(len(customers)))
        .replace("{{ORDERS_COUNT}}", str(order_count))
        .replace("{{SETTLEMENT_RATE}}", f"{settlement_rate:.1f}%")
        .replace("{{AVG_TXN}}", f"${float(avg_ticket):,.2f}")
        .replace("{{TABLE_ROWS}}", rows_html if rows_html else "<tr><td colspan='5' class='py-8 text-center text-slate-400 text-sm'>No transactions recorded yet.</td></tr>")
        .replace("{{CUSTOMER_OPTIONS}}", options_html)
    )
    return HTMLResponse(content=rendered)

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

@app.get("/api/v1/orders", response_model=list[OrderResponse], tags=["Transactions"])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id).all()

@app.post("/api/v1/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Transactions"])
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Account holder not found")
    
    order = Order(
        customer_id=payload.customer_id,
        total_amount=payload.total_amount,
        status=payload.status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
