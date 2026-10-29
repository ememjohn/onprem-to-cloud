-- 1. Table: customers
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table: orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Deterministic Seed Data: 3 Customers
INSERT INTO customers (id, name, email, created_at) VALUES
    (1, 'Acme Industrial Supplies', 'procurement@acme-industrial.example', '2026-01-10 08:30:00+00'),
    (2, 'Globex Logistics Corp', 'ops@globex-logistics.example', '2026-01-12 11:45:00+00'),
    (3, 'Soylent Foods Ltd', 'supplychain@soylent-foods.example', '2026-01-15 14:10:00+00')
ON CONFLICT (id) DO NOTHING;

-- 4. Deterministic Seed Data: 4 Orders
INSERT INTO orders (id, customer_id, total_amount, status, created_at) VALUES
    (1, 1, 1450.50, 'COMPLETED', '2026-02-01 09:15:00+00'),
    (2, 1, 320.00,  'SHIPPED',   '2026-02-03 14:20:00+00'),
    (3, 2, 8920.00, 'PROCESSING','2026-02-05 16:00:00+00'),
    (4, 3, 450.75,  'PENDING',   '2026-02-06 10:30:00+00')
ON CONFLICT (id) DO NOTHING;

-- 5. Explicitly synchronize sequence counters
SELECT setval('customers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM customers));
SELECT setval('orders_id_seq', (SELECT COALESCE(MAX(id), 1) FROM orders));
