import pytest
import httpx

BASE_URL = "http://localhost:8000"

def test_health_check_returns_healthy_and_connected():
    response = httpx.get(f"{BASE_URL}/healthz", timeout=5.0)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"
    assert payload["environment"] == "onprem-source"

def test_customers_list_contains_deterministic_seed_records():
    response = httpx.get(f"{BASE_URL}/api/v1/customers", timeout=5.0)
    assert response.status_code == 200
    customers = response.json()
    assert len(customers) >= 3
    customer_names = [customer["name"] for customer in customers]
    assert "Acme Industrial Supplies" in customer_names
    assert "Globex Logistics Corp" in customer_names
    assert "Soylent Foods Ltd" in customer_names

def test_orders_list_contains_baseline_records():
    response = httpx.get(f"{BASE_URL}/api/v1/orders", timeout=5.0)
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 4
    statuses = [order["status"] for order in orders]
    assert "COMPLETED" in statuses
    assert "SHIPPED" in statuses
    assert "PROCESSING" in statuses

def test_create_order_persists_successfully():
    new_order = {
        "customer_id": 1,
        "total_amount": 99.99,
        "status": "PENDING"
    }
    response = httpx.post(f"{BASE_URL}/api/v1/orders", json=new_order, timeout=5.0)
    assert response.status_code == 201
    created = response.json()
    assert created["customer_id"] == 1
    assert float(created["total_amount"]) == 99.99
    assert created["status"] == "PENDING"
    assert "id" in created
