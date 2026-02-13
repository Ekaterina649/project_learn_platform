import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=None):
    """Создание продукта в Stripe"""
    product_data = {
        "name": name,
    }

    if description and description.strip():
        product_data["description"] = description.strip()

    return stripe.Product.create(**product_data)


def create_stripe_price(product_id, amount):
    """Создание цены в Stripe"""
    return stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),  # рубли в копейки
        currency="rub"
    )


def create_stripe_session(price_id, success_url=None, cancel_url=None):
    """Создание сессии оплаты в Stripe"""
    return stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url or "http://127.0.0.1:8000/",
        cancel_url=cancel_url or "http://127.0.0.1:8000/",
    )