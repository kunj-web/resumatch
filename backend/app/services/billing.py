from app.core.config import settings


def is_razorpay_configured() -> bool:
    return all(
        [
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
            settings.RAZORPAY_PLAN_ID,
            settings.RAZORPAY_WEBHOOK_SECRET,
        ]
    )


def razorpay_checkout_status() -> dict:
    if not is_razorpay_configured():
        return {
            "status": "not_configured",
            "provider": "razorpay",
            "message": "Razorpay checkout is not configured yet.",
            "checkout_url": None,
        }

    return {
        "status": "ready_for_checkout_build",
        "provider": "razorpay",
        "message": "Razorpay configuration is present. Checkout creation is not connected yet.",
        "checkout_url": None,
    }
