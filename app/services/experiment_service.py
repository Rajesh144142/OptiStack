from typing import Optional, List
from app.schemas.experiment import ExperimentCreate, ExperimentResponse
from app.models.experiment import Experiment
from app.db.postgres import get_postgres_async_session, check_postgres_health
from app.core.exceptions import (
    DatabaseConnectionError,
    ExperimentNotFoundError,
    ExperimentExecutionError,
    InvalidDatabaseTypeError,
    BenchmarkError
)
from app.core.logging import logger
from app.utils.performance_monitor import PerformanceMonitor
from benchmarks.postgres_benchmark import PostgresBenchmark
from benchmarks.mysql_benchmark import MySQLBenchmark
from benchmarks.cockroachdb_benchmark import CockroachDBBenchmark
from benchmarks.mongodb_benchmark import MongoDBBenchmark
from benchmarks.redis_benchmark import RedisBenchmark
from benchmarks.cassandra_benchmark import CassandraBenchmark
from benchmarks.influxdb_benchmark import InfluxDBBenchmark
from benchmarks.elasticsearch_benchmark import ElasticsearchBenchmark
import uuid
from datetime import datetime

class ExperimentService:
    def __init__(self):
        self.benchmark_classes = {
            "postgres": PostgresBenchmark,
            "mysql": MySQLBenchmark,
            "cockroachdb": CockroachDBBenchmark,
            "mongodb": MongoDBBenchmark,
            "redis": RedisBenchmark,
            "cassandra": CassandraBenchmark,
            "influxdb": InfluxDBBenchmark,
            "elasticsearch": ElasticsearchBenchmark
        }
    
    async def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        if not await check_postgres_health():
            raise DatabaseConnectionError("PostgreSQL connection not available")
        
        if experiment.database_type.lower() not in self.benchmark_classes:
            raise InvalidDatabaseTypeError(
                f"Unsupported database type: {experiment.database_type}. "
                f"Supported types: {', '.join(self.benchmark_classes.keys())}"
            )
        
        experiment_id = str(uuid.uuid4())
        session = get_postgres_async_session()
        if not session:
            raise DatabaseConnectionError("Failed to create database session")
        
        try:
            experiment_data = Experiment(
                id=experiment_id,
                name=experiment.name,
                database_type=experiment.database_type.lower(),
                status="pending",
                created_at=datetime.utcnow(),
                config=experiment.config,
                results=None
            )
            session.add(experiment_data)
            await session.commit()
            await session.refresh(experiment_data)
            
            logger.info(f"Created experiment: {experiment_id} for database: {experiment.database_type}")
            
            return ExperimentResponse(
                id=experiment_data.id,
                name=experiment_data.name,
                database_type=experiment_data.database_type,
                status=experiment_data.status,
                created_at=experiment_data.created_at,
                config=experiment_data.config,
                results=experiment_data.results
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create experiment: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to create experiment: {e}")
        finally:
            await session.close()
    
    async def get_experiment(self, experiment_id: str) -> Optional[ExperimentResponse]:
        if not await check_postgres_health():
            raise DatabaseConnectionError("PostgreSQL connection not available")
        
        session = get_postgres_async_session()
        if not session:
            raise DatabaseConnectionError("Failed to create database session")
        
        try:
            from sqlalchemy import select
            result = await session.execute(select(Experiment).filter(Experiment.id == experiment_id))
            experiment = result.scalar_one_or_none()
            if not experiment:
                return None
            
            return ExperimentResponse(
                id=experiment.id,
                name=experiment.name,
                database_type=experiment.database_type,
                status=experiment.status,
                created_at=experiment.created_at,
                config=experiment.config,
                results=experiment.results
            )
        except Exception as e:
            logger.error(f"Failed to get experiment {experiment_id}: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to retrieve experiment: {e}")
        finally:
            await session.close()
    
    async def list_experiments(self) -> List[ExperimentResponse]:
        if not await check_postgres_health():
            raise DatabaseConnectionError("PostgreSQL connection not available")
        
        session = get_postgres_async_session()
        if not session:
            raise DatabaseConnectionError("Failed to create database session")
        
        try:
            from sqlalchemy import select
            result = await session.execute(select(Experiment))
            experiments = result.scalars().all()
            return [
                ExperimentResponse(
                    id=exp.id,
                    name=exp.name,
                    database_type=exp.database_type,
                    status=exp.status,
                    created_at=exp.created_at,
                    config=exp.config,
                    results=exp.results
                )
                for exp in experiments
            ]
        except Exception as e:
            logger.error(f"Failed to list experiments: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to list experiments: {e}")
        finally:
            await session.close()
    
    async def execute_experiment(self, experiment_id: str) -> ExperimentResponse:
        if not await check_postgres_health():
            raise DatabaseConnectionError("PostgreSQL connection not available")
        
        session = get_postgres_async_session()
        if not session:
            raise DatabaseConnectionError("Failed to create database session")
        
        try:
            from sqlalchemy import select
            result = await session.execute(select(Experiment).filter(Experiment.id == experiment_id))
            experiment = result.scalar_one_or_none()
            if not experiment:
                raise ExperimentNotFoundError(f"Experiment with id {experiment_id} not found")
            
            if experiment.status == "running":
                raise ExperimentExecutionError(f"Experiment {experiment_id} is already running")
            
            benchmark_class = self.benchmark_classes.get(experiment.database_type.lower())
            if not benchmark_class:
                raise InvalidDatabaseTypeError(
                    f"Unsupported database type: {experiment.database_type}"
                )
            
            experiment.status = "running"
            await session.commit()
            await session.refresh(experiment)
            logger.info(f"Starting experiment {experiment_id} for database {experiment.database_type}")
            
            monitor = PerformanceMonitor()
            benchmark = benchmark_class()
            benchmark.set_monitor(monitor)
            
            try:
                monitor.start_experiment()
                await benchmark.setup(experiment.config)
                benchmark_results = await benchmark.run(experiment.config)
                await benchmark.teardown()
                monitor.stop_experiment()
                
                performance_metrics = monitor.get_results()
                
                experiment.status = "completed"
                experiment.results = {
                    "benchmark_results": benchmark_results,
                    "performance_metrics": performance_metrics
                }
                await session.commit()
                await session.refresh(experiment)
                logger.info(f"Experiment {experiment_id} completed successfully")
            except Exception as e:
                experiment.status = "failed"
                experiment.results = {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                await session.commit()
                logger.error(f"Experiment {experiment_id} failed: {e}", exc_info=True)
                raise BenchmarkError(f"Benchmark execution failed: {e}") from e
            
            return ExperimentResponse(
                id=experiment.id,
                name=experiment.name,
                database_type=experiment.database_type,
                status=experiment.status,
                created_at=experiment.created_at,
                config=experiment.config,
                results=experiment.results
            )
        except (ExperimentNotFoundError, ExperimentExecutionError, InvalidDatabaseTypeError, BenchmarkError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing experiment {experiment_id}: {e}", exc_info=True)
            raise ExperimentExecutionError(f"Failed to execute experiment: {e}")
        finally:
            await session.close()

