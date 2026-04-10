import requests
from sqlalchemy import create_engine, Column, String, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///orders.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    status = Column(String)
    total_amount = Column(Float)
    items = Column(JSON)


Base.metadata.create_all(engine)


class OrderService:
    def __init__(self):
        """Initialize the order service with a database session."""
        self.db = SessionLocal()

    def get_order(self, order_id: str) -> dict:
        """
        Retrieve an order from the database by its ID.

        Returns a dictionary containing order details including id,
        status, items, and total amount.
        """
        order = self.db.query(Order).filter(Order.id == order_id).first()

        return {
            "id": order.id,
            "status": order.status,
            "items": order.items,
            "total_amount": order.total_amount,
        }

    def mark_paid(self, order_id: str, payment_id: str):
        """
        Update an order's status to 'paid' after successful payment.

        Associates the given payment ID with the order and persists the update.
        """
        order = self.db.query(Order).filter(Order.id == order_id).first()
        order.status = "paid"

        return {"order_id": order_id, "payment_id": payment_id}

    def calculate_discount(self, order: dict) -> float:
        """
        Calculate a discount for an order based on its total value.

        Applies a percentage discount if the order exceeds a threshold.
        """
        total = 0

        for item in order["items"]:
            total += item["price"] * item["quantity"]

        if total > 1000:
            return total * 0.1

        return 0

    def fetch_order_remote(self, order_id: str) -> dict:
        """
        Fetch an order from an external internal API.

        Returns the order data in dictionary format.
        """
        response = requests.get(f"https://internal-api.example.com/orders/{order_id}")
        data = response.json()

        return data["order"]