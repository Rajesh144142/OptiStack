from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.experiment import ExperimentCreate, ExperimentResponse
from app.services.experiment_service import ExperimentService
from app.core.exceptions import ExperimentNotFoundError

router = APIRouter()

@router.post("/", response_model=ExperimentResponse, summary="Create a new experiment")
async def create_experiment(experiment: ExperimentCreate):
    service = ExperimentService()
    return await service.create_experiment(experiment)

@router.get("/", response_model=list[ExperimentResponse], summary="List all experiments")
async def list_experiments():
    service = ExperimentService()
    return await service.list_experiments()

@router.get("/{experiment_id}", response_model=ExperimentResponse, summary="Get experiment by ID")
async def get_experiment(experiment_id: str):
    service = ExperimentService()
    experiment = await service.get_experiment(experiment_id)
    if not experiment:
        raise ExperimentNotFoundError(f"Experiment with id {experiment_id} not found")
    return experiment

@router.post("/{experiment_id}/run", response_model=ExperimentResponse, summary="Execute an experiment")
async def run_experiment(experiment_id: str, background_tasks: BackgroundTasks):
    service = ExperimentService()
    return await service.execute_experiment(experiment_id)

