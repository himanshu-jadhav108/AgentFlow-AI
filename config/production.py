"""Production configuration profile overrides."""

OVERRIDES = {
    "LOG_LEVEL": "INFO",
    "ENABLE_CACHE": True,
    "CACHE_TTL_SECONDS": 600,
    "MAX_PAYLOAD_SIZE_BYTES": 512 * 1024,  # Restricted to 512KB for api security
    "DEBUG_MODE": False,
    "ENABLE_DASHBOARD": False,
    "EXPOSE_DEBUG_ENDPOINTS": False,
}
