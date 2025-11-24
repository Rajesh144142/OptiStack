from typing import Optional, List
from app.schemas.experiment import ExperimentCreate, ExperimentResponse
from app.models.experiment import Experiment
import uuid
from datetime import datetime

class ExperimentService:
    async def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        experiment_id = str(uuid.uuid4())
        experiment_data = Experiment(
            id=experiment_id,
            name=experiment.name,
            database_type=experiment.database_type,
            status="pending",
            created_at=datetime.utcnow(),
            config=experiment.config,
            results=None
        )
        return ExperimentResponse(
            id=experiment_data.id,
            name=experiment_data.name,
            database_type=experiment_data.database_type,
            status=experiment_data.status,
            created_at=experiment_data.created_at,
            config=experiment_data.config,
            results=experiment_data.results
        )
    
    async def get_experiment(self, experiment_id: str) -> Optional[ExperimentResponse]:
        return None
    
    async def list_experiments(self) -> List[ExperimentResponse]:
        return []

