from app.core.config import settings

AUTONOMY_ACTOR_TYPE = "autonomy"


def canonical_actor_type(actor_type: str) -> str:
    """Normalize write actors and gate autonomous canonical writes behind one switch."""
    normalized = actor_type.strip().casefold()
    if not normalized:
        raise PermissionError("actor_type is required for canonical writes")
    if normalized == "ai":
        if not settings.autonomy_mode_enabled:
            raise PermissionError("AI canonical writes require AUTONOMY_MODE_ENABLED=true")
        return AUTONOMY_ACTOR_TYPE
    if normalized == AUTONOMY_ACTOR_TYPE and not settings.autonomy_mode_enabled:
        raise PermissionError("Autonomy canonical writes require AUTONOMY_MODE_ENABLED=true")
    return normalized
