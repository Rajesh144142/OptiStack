# OptiStack

OptiStack is a **performance experimentation tool** that allows you to conduct experiments against different data stores like MySQL, Redis, MongoDB, DynamoDB, PostgreSQL, Cassandra, and CockroachDB. It provides a flexible and extensible framework for running performance experiments and analyzing the results.

## Features

- Conduct performance experiments against various data stores
- Easily configure experiment parameters such as the number of rows, concurrent queries, and more
- Run experiments locally or deploy them to a cloud environment
- Analyze experiment results to identify performance bottlenecks and optimize system performance
- Real-time metrics monitoring (CPU usage, memory consumption, endpoint latency, request throughput)
- Query and endpoint profiling to track slow operations
- Distributed tracing using OpenTelemetry

## Tech Stack

**Backend:**
- Python
- FastAPI
- Uvicorn / Gunicorn

**Supported Databases:**
- PostgreSQL
- Cassandra
- CockroachDB
- MySQL
- Redis
- MongoDB
- DynamoDB

**Monitoring & Metrics:**
- OpenTelemetry
- Prometheus (optional)
- Grafana (optional)

## Getting Started

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

### Quick Start with Docker

1. **Install Docker Desktop** and make sure it's running

2. **Clone and start:**
   ```bash
   git clone https://github.com/Rajesh144142/OptiStack.git
   cd OptiStack
   docker-compose up -d
   ```

3. **Initialize Cassandra:**
   ```bash
   docker-compose exec app sh -c "PYTHONPATH=/app python scripts/init_cassandra.py"
   ```

4. **Access API:** http://localhost:8000/docs

That's it! All databases and the application are now running.

For local development setup or troubleshooting, see [SETUP.md](SETUP.md)

## Configuration

You can configure various aspects of the experiment, such as:
- Number of rows to process
- Concurrent queries
- Data store connection settings
- Experiment parameters

Configuration files are located in the `conf` directory.

## Project Structure

The project follows a clean, layered architecture pattern with clear separation of concerns:

```
OptiStack/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # API router configuration
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── experiments.py # Experiment endpoints
│   │           └── health.py      # Health check endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Application settings
│   │   └── logging.py              # Logging configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── experiment.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── experiment.py          # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── experiment_service.py  # Business logic layer
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # Database base configuration
│   │   ├── postgres.py            # PostgreSQL connection
│   │   ├── mysql.py               # MySQL connection
│   │   ├── mongodb.py             # MongoDB connection
│   │   └── redis.py               # Redis connection
│   └── utils/
│       ├── __init__.py
│       └── helpers.py              # Utility functions
├── benchmarks/
│   ├── __init__.py
│   ├── base.py                    # Base benchmark abstract class
│   ├── postgres_benchmark.py
│   ├── mysql_benchmark.py
│   ├── mongodb_benchmark.py
│   └── redis_benchmark.py
├── telemetry/
│   ├── __init__.py
│   ├── tracing.py                 # OpenTelemetry tracing
│   └── metrics.py                 # Metrics collection
├── conf/
│   ├── __init__.py
│   └── config.yaml                # Configuration file
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_api/
│   │   ├── __init__.py
│   │   └── test_experiments.py
│   └── test_services/
│       ├── __init__.py
│       └── test_experiment_service.py
├── scripts/
│   ├── __init__.py
│   └── setup_db.py                # Database setup script
├── .gitignore
├── requirements.txt
├── pyproject.toml                 # Modern Python project config
├── Dockerfile
├── docker-compose.yml
├── env.example                    # Environment variables template
└── README.md
```

### Architecture Overview

- **API Layer** (`app/api/`): Handles HTTP requests and responses, routes to appropriate endpoints
- **Service Layer** (`app/services/`): Contains business logic and orchestrates operations
- **Model Layer** (`app/models/`): Database models using SQLAlchemy ORM
- **Schema Layer** (`app/schemas/`): Pydantic models for request/response validation
- **Database Layer** (`app/db/`): Database connection management for different data stores
- **Benchmarks** (`benchmarks/`): Performance testing implementations for each database
- **Telemetry** (`telemetry/`): Observability and monitoring setup
- **Tests** (`tests/`): Test suite organized to mirror application structure

## Roadmap

- [ ] Add Redis benchmark module
- [ ] Add load-testing suite (k6)
- [ ] Add CPU/Memory flamegraph generation
- [ ] Add WebSocket-based live metrics streaming
- [ ] Build frontend dashboard (React)
- [ ] Add more database connectors

## Contributing

Contributions are welcome! Please feel free to submit bug reports, feature requests, or pull requests on the GitHub repository.

For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License
