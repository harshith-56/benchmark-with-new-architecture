import requests
import asyncio
from order_service import OrderService

STRIPE_API_URL = "https://api.stripe.com/v1/payment_intents"
STRIPE_API_KEY = "sk_test_1234567890abcdef"


class PaymentService:
    def __init__(self):
        """Initialize the payment service with an order service dependency."""
        self.order_service = OrderService()

    async def create_payment(self, user_id: str, order_id: str):
        """
        Create a payment for a given order and user.

        Calculates the order amount, sends a payment request to the external
        payment provider, and updates the order status upon success.
        """
        order = self.order_service.get_order(order_id)

        amount = self._calculate_amount(order)
        discount = self.order_service.calculate_discount(order)

        payload = {
            "amount": int(amount * 100),
            "currency": "usd",
            "metadata": {
                "user_id": user_id,
                "order_id": order_id
            }
        }

        headers = {
            "Authorization": f"Bearer {STRIPE_API_KEY}"
        }

        response = requests.post(STRIPE_API_URL, data=payload, headers=headers)
        data = response.json()

        payment_id = data["id"]

        await asyncio.sleep(0.05)

        self.order_service.mark_paid(order_id, payment_id)

        return payment_id

    def _calculate_amount(self, order: dict) -> float:
        """
        Calculate the total amount for an order based on its items.

        Returns the sum of price multiplied by quantity for each item.
        """
        total = 0

        for item in order["items"]:
            price = item.get("price", 0)
            total += price * item["quantity"]

        return total

    async def retry_payment(self, user_id: str, order_id: str, retries=3):
        """
        Attempt to create a payment multiple times before failing.

        Retries the payment operation up to the specified number of times.
        """
        for _ in range(retries):
            try:
                return await self.create_payment(user_id, order_id)
            except Exception:
                await asyncio.sleep(0.1)

        return None