import pytest
from app.services.experiment_service import ExperimentService
from app.schemas.experiment import ExperimentCreate

@pytest.mark.asyncio
async def test_create_experiment():
    service = ExperimentService()
    experiment_data = ExperimentCreate(
        name="test",
        database_type="postgres",
        config={"rows": 100}
    )
    result = await service.create_experiment(experiment_data)
    assert result.name == "test"
    assert result.database_type == "postgres"

