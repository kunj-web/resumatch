from datetime import datetime, timedelta
from typing import Dict, Tuple
import uuid

# In-memory store: {user_id: [(timestamp, endpoint)]}
rate_limit_store: Dict[uuid.UUID, list] = {}

# Rate limit config
RATE_LIMITS = {
    "extract_job": {"calls": 10, "period": 3600},  # 10 call per hour
    "improve_resume": {"calls": 5, "period": 3600},  # 5 calls per hour
}


def check_rate_limit(user_id: uuid.UUID, endpoint: str) -> Tuple[bool, dict]:
    """
    Check if user has exceeded rate limit.
    Returns (is_allowed, info_dict)
    """
    if endpoint not in RATE_LIMITS:
        return True, {}

    limit_config = RATE_LIMITS[endpoint]
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=limit_config["period"])

    # Get or create user's request history
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []

    # Clean old requests
    rate_limit_store[user_id] = [
        (timestamp, ep)
        for timestamp, ep in rate_limit_store[user_id]
        if timestamp > cutoff
    ]

    # Count requests for this endpoint
    recent_calls = sum(1 for _, ep in rate_limit_store[user_id] if ep == endpoint)

    # Check if over limit
    if recent_calls >= limit_config["calls"]:
        remaining_wait = int((rate_limit_store[user_id][0][0] - cutoff).total_seconds())
        return False, {
            "limit": limit_config["calls"],
            "period": limit_config["period"],
            "retry_after": remaining_wait,
        }

    # Add current request
    rate_limit_store[user_id].append((now, endpoint))
    return True, {
        "remaining": limit_config["calls"] - recent_calls - 1,
        "limit": limit_config["calls"],
    }
