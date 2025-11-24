from app.core.config import settings

def setup_tracing():
    if not settings.OPENTELEMETRY_ENABLED:
        return
    
    pass

def get_tracer(name: str):
    return None

