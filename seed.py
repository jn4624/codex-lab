"""Populate customer.db with deterministic Korean practice data.

Running this script replaces the rows in the four practice tables.
"""

import random
from datetime import date, datetime, timedelta

from faker import Faker
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert

from database import DATABASE_PATH, SessionLocal, engine, init_db
from models import Customer, Employee, Order, Product

SEED = 20261110
# Fixed anchor keeps the generated dataset reproducible and within the requested
# two-year window as of 2026-11-10.
DATE_END = datetime(2026, 11, 10, 23, 59, 59)
DATE_START = DATE_END - timedelta(days=365 * 2)
CATEGORIES = ["전자제품", "생활용품", "식품", "의류", "도서"]


def ensure_columns() -> None:
    """Add new seed fields when using a DB created from an older model version."""
    with engine.begin() as connection:
        customer_columns = {
            row["name"] for row in connection.execute(text("PRAGMA table_info(customers)")).mappings()
        }
        if "tier" not in customer_columns:
            connection.execute(
                text("ALTER TABLE customers ADD COLUMN tier TEXT NOT NULL DEFAULT '일반'")
            )

        order_columns = {
            row["name"] for row in connection.execute(text("PRAGMA table_info(orders)")).mappings()
        }
        if "total_amount" not in order_columns:
            connection.execute(
                text("ALTER TABLE orders ADD COLUMN total_amount REAL NOT NULL DEFAULT 0")
            )


def make_datetime(fake: Faker, start: datetime, end: datetime) -> str:
    """Generate a deterministic ISO 8601 timestamp in the requested period."""
    return fake.date_time_between(start_date=start, end_date=end).isoformat(sep=" ", timespec="seconds")


def seed_database() -> None:
    random.seed(SEED)
    fake = Faker("ko_KR")
    fake.seed_instance(SEED)

    init_db()
    ensure_columns()
    with SessionLocal() as session:
        # Clear in FK-safe order so reruns always produce the same dataset.
        session.query(Order).delete(synchronize_session=False)
        session.query(Customer).delete(synchronize_session=False)
        session.query(Product).delete(synchronize_session=False)
        session.query(Employee).delete(synchronize_session=False)
        session.commit()

        customer_tiers = ["VIP"] * 500 + ["일반"] * 7_000 + ["신규"] * 2_500
        random.shuffle(customer_tiers)
        customers = [
            {
                "customer_id": customer_id,
                "name": fake.name(),
                "email": f"customer{customer_id:05d}@example.kr",
                "phone": fake.phone_number(),
                "address": fake.address(),
                "created_at": make_datetime(fake, DATE_START, DATE_END),
                "tier": customer_tiers[customer_id - 1],
            }
            for customer_id in range(1, 10_001)
        ]
        products = []
        for product_id in range(1, 501):
            category = random.choice(CATEGORIES)
            products.append(
                {
                    "product_id": product_id,
                    "name": f"{category} 상품 {product_id:03d}",
                    "category": category,
                    "unit_price": random.randint(1_000, 2_000_000),
                    "stock_quantity": random.randint(0, 5_000),
                }
            )
        employees = [
            {
                "employee_id": employee_id,
                "name": fake.name(),
                "email": f"employee{employee_id:03d}@example.kr",
                "department": random.choice(["영업", "고객지원", "운영", "물류"]),
                "hire_date": fake.date_between(
                    start_date=date(2006, 11, 10), end_date=DATE_END.date()
                ).isoformat(),
            }
            for employee_id in range(1, 301)
        ]

        # Core bulk inserts: each execute sends a list of mappings, not one ORM
        # add/commit per row.
        session.execute(insert(Customer), customers)
        session.execute(insert(Product), products)
        session.execute(insert(Employee), employees)

        product_by_id = {product["product_id"]: product for product in products}
        order_statuses = ["완료"] * 90_000 + ["배송중"] * 7_000 + ["취소"] * 3_000
        random.shuffle(order_statuses)
        orders = []
        total_seconds = int((DATE_END - DATE_START).total_seconds())
        for order_id in range(1, 100_001):
            product_id = random.randint(1, 500)
            quantity = random.randint(1, 5)
            unit_price = product_by_id[product_id]["unit_price"]
            order_date = DATE_START + timedelta(seconds=random.randint(0, total_seconds))
            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": random.randint(1, 10_000),
                    "product_id": product_id,
                    "employee_id": random.randint(1, 300),
                    "order_date": order_date.isoformat(sep=" ", timespec="seconds"),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "status": order_statuses[order_id - 1],
                    "total_amount": unit_price * quantity,
                }
            )

        # Chunked executemany bulk insert keeps memory and SQLite statement size
        # bounded while avoiding per-row inserts.
        for offset in range(0, len(orders), 5_000):
            session.execute(insert(Order), orders[offset : offset + 5_000])
        session.commit()

    with engine.connect() as connection:
        counts = {
            table: connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            for table in ("customers", "products", "employees", "orders")
        }
    print(f"Seeded {DATABASE_PATH}")
    for table, count in counts.items():
        print(f"{table}: {count:,}")


if __name__ == "__main__":
    seed_database()
