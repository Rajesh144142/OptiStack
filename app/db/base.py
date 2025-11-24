from app.models.experiment import Base

def init_db():
    Base.metadata.create_all(bind=None)

