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
        badge_cls = "pill-settled" if o.status == "SETTLED" else ("pill-completed" if o.status == "COMPLETED" else "pill-processing")
        cust_name = o.customer.name if o.customer else f"Account #{o.customer_id}"
        date_str = o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else "Pending"
        
        rows_html += f"""
        <tr class="ledger-row border-b border-white/[0.045] hover:bg-white/[0.03]">
            <td class="px-4 py-3 whitespace-nowrap font-mono text-[12.5px] text-ink/90">TXN-{o.id:04d}</td>
            <td class="px-4 py-3 text-[13px] font-medium text-ink">{cust_name}</td>
            <td class="px-4 py-3 font-mono text-[11.5px] text-dim whitespace-nowrap">ACCT-00{o.customer_id}</td>
            <td class="px-4 py-3 text-right font-mono tabnum text-[13.5px] font-semibold text-ink">${float(o.total_amount):,.2f}</td>
            <td class="px-4 py-3"><span class="pill {badge_cls}"><span class="pill-dot"></span>{o.status}</span></td>
            <td class="px-4 py-3 font-mono tabnum text-[11px] text-faint whitespace-nowrap">{date_str}</td>
        </tr>
        """
        
    options_html = "".join([f"<option value='{c.id}'>{c.name} · ACCT-00{c.id}</option>" for c in customers])
    
    if not TEMPLATE_FILE.exists():
        return HTMLResponse(content="<h1>Dashboard template missing</h1>", status_code=500)
        
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    rendered = (
        template.replace("{{TOTAL_VOLUME}}", f"${float(total_volume):,.2f}")
        .replace("{{CUSTOMERS_COUNT}}", str(len(customers)))
        .replace("{{ORDERS_COUNT}}", str(order_count))
        .replace("{{SETTLEMENT_RATE}}", f"{settlement_rate:.1f}%")
        .replace("{{AVG_TXN}}", f"${float(avg_ticket):,.2f}")
        .replace("{{TABLE_ROWS}}", rows_html if rows_html else "<tr><td colspan='6' class='py-8 text-center text-slate-500 text-sm'>No records found.</td></tr>")
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