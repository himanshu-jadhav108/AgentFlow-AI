"""Testing configuration profile overrides."""

OVERRIDES = {
    "LOG_LEVEL": "DEBUG",
    "ENABLE_CACHE": False,  # Disabled to verify grounding queries fresh
    "RATE_LIMIT_REQUESTS": 1000,  # Prevents test rate-limiting collisions
}
