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


def _base_checkout_payload(status: str, message: str) -> dict:
    return {
        "status": status,
        "provider": "razorpay",
        "message": message,
        "checkout_url": None,
    }


def razorpay_checkout_status() -> dict:
    if not is_razorpay_configured():
        return _base_checkout_payload(
            "not_configured",
            "Razorpay checkout is not configured yet.",
        )

    return _base_checkout_payload(
        "ready_for_checkout_build",
        "Razorpay configuration is present.",
    )


def create_razorpay_checkout(user) -> dict:
    if not is_razorpay_configured():
        return razorpay_checkout_status()

    try:
        import razorpay
    except ImportError:
        return _base_checkout_payload(
            "sdk_missing",
            "Razorpay SDK is not installed in the backend environment.",
        )

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    subscription = client.subscription.create(
        {
            "plan_id": settings.RAZORPAY_PLAN_ID,
            "total_count": 12,
            "customer_notify": 1,
            "notes": {
                "user_id": str(user.id),
                "email": user.email,
                "source": "resumatch_pro_upgrade",
            },
        }
    )

    subscription_id = subscription.get("id")
    if not subscription_id:
        return _base_checkout_payload(
            "provider_error",
            "Razorpay did not return a subscription id.",
        )

    return {
        "status": "checkout_created",
        "provider": "razorpay",
        "message": "Razorpay checkout is ready.",
        "checkout_url": None,
        "key_id": settings.RAZORPAY_KEY_ID,
        "subscription_id": subscription_id,
        "checkout_options": {
            "key": settings.RAZORPAY_KEY_ID,
            "subscription_id": subscription_id,
            "name": "ResuMatch Pro",
            "description": "Pro plan subscription",
            "prefill": {
                "name": user.full_name,
                "email": user.email,
            },
            "notes": {
                "user_id": str(user.id),
            },
        },
    }
