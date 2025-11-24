from fastapi import APIRouter, HTTPException
from app.schemas.experiment import ExperimentCreate, ExperimentResponse
from app.services.experiment_service import ExperimentService

router = APIRouter()

@router.post("/", response_model=ExperimentResponse)
async def create_experiment(experiment: ExperimentCreate):
    service = ExperimentService()
    return await service.create_experiment(experiment)

@router.get("/", response_model=list[ExperimentResponse])
async def list_experiments():
    service = ExperimentService()
    return await service.list_experiments()

@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str):
    service = ExperimentService()
    experiment = await service.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

