from sqlalchemy import case, create_engine, func, select
from sqlalchemy.orm import Session

from models import Base, Customer, Order


def test_tier_report_metric_definitions_and_cancelled_revenue_exclusion():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        vip = Customer(customer_id=1, name="VIP 고객", created_at="2026-01-01", tier="VIP")
        ordinary = Customer(customer_id=2, name="일반 고객", created_at="2026-01-01", tier="일반")
        no_order = Customer(customer_id=3, name="신규 고객", created_at="2026-01-01", tier="신규")
        session.add_all([vip, ordinary, no_order])
        session.flush()
        session.add_all(
            [
                Order(order_id=1, customer_id=1, product_id=1, employee_id=1,
                      order_date="2026-01-02", quantity=1, unit_price=100,
                      status="완료", total_amount=100),
                Order(order_id=2, customer_id=1, product_id=1, employee_id=1,
                      order_date="2026-01-03", quantity=1, unit_price=50,
                      status="취소", total_amount=50),
                Order(order_id=3, customer_id=2, product_id=1, employee_id=1,
                      order_date="2026-01-04", quantity=1, unit_price=25,
                      status="배송중", total_amount=25),
            ]
        )
        session.commit()

        customer_counts = dict(
            session.execute(
                select(Customer.tier, func.count(Customer.customer_id)).group_by(Customer.tier)
            ).all()
        )
        order_metrics = session.execute(
            select(
                Customer.tier,
                func.count(Order.order_id),
                func.sum(case((Order.status == "완료", 1), else_=0)),
                func.sum(case((Order.status == "배송중", 1), else_=0)),
                func.sum(case((Order.status == "취소", 1), else_=0)),
                func.coalesce(
                    func.sum(case((Order.status != "취소", Order.total_amount), else_=0)), 0
                ),
            )
            .outerjoin(Order, Customer.customer_id == Order.customer_id)
            .group_by(Customer.tier)
        ).all()

    assert customer_counts == {"VIP": 1, "일반": 1, "신규": 1}
    metrics = {row[0]: row[1:] for row in order_metrics}
    assert metrics["VIP"] == (2, 1, 0, 1, 100)
    assert metrics["일반"] == (1, 0, 1, 0, 25)
    assert metrics["신규"] == (0, 0, 0, 0, 0)
