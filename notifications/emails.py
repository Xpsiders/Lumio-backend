from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    send_mail(
        subject='Welcome to Lumio!',
        message=f'Hi {user.first_name or user.email}, welcome to Lumio. Start shopping the best tech gadgets today!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True
    )

def send_order_confirmation_email(order):
    items_text = '\n'.join([
        f"- {item.product_name} x{item.quantity} — ${item.product_price}"
        for item in order.items.all()
    ])

    message = f"""
Hi {order.user.first_name or order.user.email},

Your order has been confirmed! Here are the details:

Order ID: {order.id}
Status: {order.status}
Shipping to: {order.shipping_address}

Items:
{items_text}

Total: ${order.total_price}

Thank you for shopping with Lumio!
    """

    send_mail(
        subject=f'Lumio — Order Confirmed #{str(order.id)[:8].upper()}',
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=True
    )

def send_order_cancelled_email(order):
    send_mail(
        subject=f'Lumio — Order Cancelled #{str(order.id)[:8].upper()}',
        message=f"""
Hi {order.user.first_name or order.user.email},

Your order #{str(order.id)[:8].upper()} has been cancelled.

If you did not request this cancellation or need help, please contact us.

Thank you,
Lumio Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=True
    )

def send_seller_new_order_email(seller, order, items):
    items_text = '\n'.join([
        f"- {item.product_name} x{item.quantity} — ${item.product_price}"
        for item in items
    ])

    send_mail(
        subject=f'Lumio — New Order Received #{str(order.id)[:8].upper()}',
        message=f"""
Hi {seller.first_name or seller.email},

You have a new order on your Lumio store!

Order ID: {str(order.id)[:8].upper()}
Customer: {order.user.email}
Shipping to: {order.shipping_address}

Your items in this order:
{items_text}

Log in to your seller dashboard to manage this order.

Lumio Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[seller.email],
        fail_silently=True
    )

def send_store_approved_email(store):
    send_mail(
        subject='Lumio — Your store has been approved!',
        message=f"""
Hi {store.owner.first_name or store.owner.email},

Great news! Your store "{store.name}" has been approved on Lumio.

You can now start listing your products and selling to customers.

Log in to your seller dashboard to get started.

Lumio Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[store.owner.email],
        fail_silently=True
    )

def send_store_suspended_email(store):
    send_mail(
        subject='Lumio — Your store has been suspended',
        message=f"""
Hi {store.owner.first_name or store.owner.email},

Your store "{store.name}" has been suspended on Lumio.

If you believe this is a mistake, please contact our support team.

Lumio Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[store.owner.email],
        fail_silently=True
    )

def send_password_changed_email(user):
    send_mail(
        subject='Lumio — Your password was changed',
        message=f"""
Hi {user.first_name or user.email},

Your Lumio account password was recently changed.

If you did not make this change, please contact us immediately.

Lumio Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True
    )