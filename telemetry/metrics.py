from app.core.config import settings

def setup_metrics():
    if not settings.OPENTELEMETRY_ENABLED:
        return
    
    pass

def record_metric(name: str, value: float, tags: dict = None):
    pass

