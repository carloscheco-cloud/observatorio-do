from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.actors import AUTONOMY_ACTOR_TYPE
from app.core.config import settings


def activate_autonomy_session(db: Session) -> str:
    """Enable the non-blocking autonomous writer identity for the current transaction."""
    if not settings.autonomy_mode_enabled:
        raise RuntimeError("AUTONOMY_MODE_ENABLED must be true")
    bind = db.get_bind()
    if bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT set_config('app.actor_type', :actor_type, true)"),
            {"actor_type": AUTONOMY_ACTOR_TYPE},
        )
    return AUTONOMY_ACTOR_TYPE
