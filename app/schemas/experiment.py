from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ExperimentCreate(BaseModel):
    name: str
    database_type: str
    config: Dict[str, Any]

class ExperimentResponse(BaseModel):
    id: str
    name: str
    database_type: str
    status: str
    created_at: datetime
    config: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

