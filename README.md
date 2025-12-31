# OptiStack

OptiStack is a **performance experimentation tool** that allows you to conduct experiments against different data stores like MySQL, Redis, MongoDB, DynamoDB, PostgreSQL, Cassandra, and CockroachDB. It provides a flexible and extensible framework for running performance experiments and analyzing the results.

## Features

- Conduct performance experiments against various data stores
- Easily configure experiment parameters such as the number of rows, concurrent queries, and more
- Run experiments locally or deploy them to a cloud environment
- Analyze experiment results to identify performance bottlenecks and optimize system performance
- Real-time metrics monitoring (CPU usage, memory consumption, endpoint latency, request throughput)
- Query and endpoint profiling to track slow operations
- Comprehensive error handling and logging
- RESTful API with OpenAPI documentation

## Tech Stack

**Backend:**
- Python
- FastAPI
- Uvicorn / Gunicorn

**Supported Databases:**

**SQL Databases:**
- **PostgreSQL** - Relational database with ACID transactions, supports complex queries, JSON, full-text search
- **MySQL** - Popular relational database, optimized for web applications and read-heavy workloads
- **CockroachDB** - Distributed SQL database with global ACID transactions, multi-region support

**NoSQL Databases:**
- **MongoDB** - Document database with flexible schema, supports nested data and aggregation pipelines
- **Redis** - In-memory key-value store, fastest for caching and real-time data (sub-millisecond latency)
- **Cassandra** - Wide-column database, optimized for high write throughput and global scale
- **InfluxDB** - Time-series database, designed for metrics, IoT data, and time-stamped measurements
- **Elasticsearch** - Search and analytics engine, full-text search, aggregations, and complex queries
- **DynamoDB** - Managed NoSQL database (AWS), auto-scaling, serverless-friendly

**Monitoring & Metrics:**
- OpenTelemetry
- Prometheus (optional)
- Grafana (optional)

## Database Types Overview

### SQL Databases (Relational)
- **PostgreSQL**: ACID-compliant relational database. Supports complex JOINs, window functions, JSON queries, full-text search. Best for: Complex queries, transactions, analytics.
- **MySQL**: Popular relational database optimized for web applications. Fast reads, query cache, multiple storage engines. Best for: Web apps, read-heavy workloads.
- **CockroachDB**: Distributed SQL database with global ACID transactions. Automatic sharding, multi-region support. Best for: Global applications, distributed systems.

### NoSQL Databases

**Document Stores:**
- **MongoDB**: Flexible JSON-like document database. Schema-less, supports nested data, aggregation pipelines, $lookup joins. Best for: Rapid development, content management, flexible schemas.

**Key-Value Stores:**
- **Redis**: In-memory key-value store. Fastest operations (sub-millisecond latency). Supports strings, hashes, sorted sets, pub/sub. Best for: Caching, session storage, real-time data.

**Wide-Column Stores:**
- **Cassandra**: Partition-based wide-column database. High write throughput, eventual consistency, no single point of failure. Best for: Time-series data, high write loads, global scale.

**Time-Series Databases:**
- **InfluxDB**: Optimized for time-stamped data. Efficient storage and queries for metrics, IoT data, monitoring. Uses Flux query language. Best for: Metrics, IoT, monitoring dashboards.

**Search Engines:**
- **Elasticsearch**: Distributed search and analytics engine. Full-text search, complex aggregations, real-time analytics. Best for: Search functionality, log analysis, data exploration.

### Key Differences: SQL vs NoSQL

| Feature | SQL Databases | NoSQL Databases |
|---------|--------------|-----------------|
| **Schema** | Fixed, defined upfront | Flexible, schema-less |
| **Consistency** | ACID transactions | Eventual consistency (most) |
| **Query Language** | SQL (standardized) | Database-specific |
| **Scaling** | Vertical (mostly) | Horizontal (designed for) |
| **Use Cases** | Complex queries, transactions | High throughput, flexible data |
| **Data Model** | Tables with relationships | Documents, key-value, wide-column |

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

**Note:** InfluxDB and Elasticsearch are automatically initialized when the containers start. No additional setup required.

For local development setup or troubleshooting, see [SETUP.md](SETUP.md)

## Usage

### API Endpoints

#### 1. Create an Experiment

```bash
POST /api/v1/experiments/
Content-Type: application/json

{
  "name": "PostgreSQL Insert Benchmark",
  "database_type": "postgres",
  "config": {
    "rows": 1000,
    "operations": ["insert", "select", "update"]
  }
}
```

**Supported Database Types:**

**SQL Databases:**
- `postgres` - PostgreSQL (Relational, ACID, complex queries, JSON support)
- `mysql` - MySQL (Relational, ACID, web-optimized)
- `cockroachdb` - CockroachDB (Distributed SQL, global ACID, multi-region)

**NoSQL Databases:**
- `mongodb` - MongoDB (Document store, flexible schema, aggregation pipelines)
- `redis` - Redis (In-memory key-value, fastest for caching, sub-millisecond)
- `cassandra` - Cassandra (Wide-column, high write throughput, eventual consistency)
- `influxdb` - InfluxDB (Time-series, optimized for metrics and IoT data)
- `elasticsearch` - Elasticsearch (Search engine, full-text search, analytics)

**Config Options:**
- `rows` (int): Number of rows/documents to process (default: 1000)
- `operations` (list): Operations to benchmark
  - **PostgreSQL**: `["insert", "select", "update", "join", "window", "json", "fulltext"]`
    - `window`: Window functions (ROW_NUMBER, LAG, LEAD, running sums)
    - `json`: JSONB queries and operations
    - `fulltext`: Full-text search with GIN indexes
  - **MySQL/CockroachDB**: `["insert", "select", "update", "join"]`
  - **CockroachDB**: Also supports `["transaction"]` for distributed transaction testing
  - **MongoDB**: `["insert", "select", "update", "aggregate", "lookup", "textsearch"]`
    - `lookup`: $lookup joins between collections
    - `textsearch`: Full-text search queries
  - **Redis**: `["set", "get", "pipeline", "hash", "sortedset"]`
    - `sortedset`: Sorted sets for leaderboards and range queries
  - **Cassandra**: `["insert", "select", "update", "consistency", "timeseries"]`
    - `consistency`: Test different consistency levels (ONE, QUORUM, ALL)
    - `timeseries`: Time-series data patterns with clustering keys
  - **InfluxDB**: `["write", "query", "aggregate"]`
    - Time-series data writes and Flux queries
  - **Elasticsearch**: `["index", "search", "aggregate", "fulltext"]`
    - Full-text search, aggregations, and complex queries

#### 2. Execute an Experiment

```bash
POST /api/v1/experiments/{experiment_id}/run
```

#### 3. Get Experiment Results

```bash
GET /api/v1/experiments/{experiment_id}
```

**Response Example:**
```json
{
  "id": "uuid",
  "name": "PostgreSQL Insert Benchmark",
  "database_type": "postgres",
  "status": "completed",
  "created_at": "2025-01-01T00:00:00",
  "config": {
    "rows": 1000,
    "operations": ["insert", "select"]
  },
  "results": {
    "benchmark_results": {
      "insert": {
        "rows_inserted": 1000,
        "time_seconds": 0.245,
        "rows_per_second": 4081.63
      },
      "select": {
        "queries_executed": 100,
        "avg_time_seconds": 0.0012,
        "min_time_seconds": 0.0008,
        "max_time_seconds": 0.0035
      }
    },
    "performance_metrics": {
      "duration_seconds": 0.456,
      "total_queries": 1100,
      "ops_per_second": 2412.28,
      "latency_ms": {
        "avg": 0.45,
        "p50": 0.42,
        "p95": 0.89,
        "p99": 1.23
      },
      "cpu_percent": {
        "avg": 25.3,
        "max": 45.2
      },
      "memory_mb": {
        "avg": 128.5,
        "max": 156.8
      }
    }
  }
}
```

#### 4. List All Experiments

```bash
GET /api/v1/experiments/
```

### Example: Complete Workflow

```bash
# 1. Create experiment
curl -X POST http://localhost:8000/api/v1/experiments/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MongoDB Test",
    "database_type": "mongodb",
    "config": {
      "rows": 5000,
      "operations": ["insert", "select", "aggregate"]
    }
  }'

# Response: {"id": "abc-123", ...}

# 2. Run experiment
curl -X POST http://localhost:8000/api/v1/experiments/abc-123/run

# 3. Check results
curl http://localhost:8000/api/v1/experiments/abc-123
```

### Interactive API Documentation

Access the interactive Swagger UI at: http://localhost:8000/docs

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=optistack

# MySQL
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=optistack

# MongoDB
MONGODB_URL=mongodb://mongodb:27017

# Redis
REDIS_URL=redis://redis:6379

# Cassandra
CASSANDRA_HOST=cassandra
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=optistack

# CockroachDB
COCKROACHDB_HOST=cockroachdb
COCKROACHDB_PORT=26257
COCKROACHDB_USER=root
COCKROACHDB_PASSWORD=
COCKROACHDB_DB=optistack

# InfluxDB (Time-series database)
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=your-token-here
INFLUXDB_ORG=optistack
INFLUXDB_BUCKET=optistack

# Elasticsearch (Search and analytics)
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=changeme

# Logging
LOG_LEVEL=INFO
```

### Configuration File

Edit `conf/config.yaml` to customize:

- Connection pool sizes
- Default experiment parameters
- Timeout settings

```yaml
experiments:
  default_rows: 1000
  default_concurrent_queries: 10
  timeout_seconds: 300

databases:
  postgres:
    pool_size: 10
    max_overflow: 20
  mysql:
    pool_size: 10
    max_overflow: 20
  mongodb:
    max_pool_size: 50
  redis:
    max_connections: 50
```

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
│       └── performance_monitor.py # Performance monitoring utility
├── benchmarks/
│   ├── __init__.py
│   ├── base.py                    # Base benchmark abstract class
│   ├── postgres_benchmark.py
│   ├── mysql_benchmark.py
│   ├── mongodb_benchmark.py
│   ├── redis_benchmark.py
│   └── cassandra_benchmark.py
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

### Folder Structure Explained

#### Application Core (`app/`)
- **`app/main.py`**: FastAPI application entry point, initializes the app and includes routers
- **`app/api/`**: API layer - handles HTTP requests and responses
  - `api/v1/`: Versioned API endpoints
  - `api/v1/endpoints/`: Individual endpoint files (experiments, health, etc.)
  - `api/v1/router.py`: Routes configuration
- **`app/core/`**: Core application configuration
  - `config.py`: Application settings and environment variables
  - `logging.py`: Logging configuration
- **`app/models/`**: Database models using SQLAlchemy ORM
- **`app/schemas/`**: Pydantic schemas for request/response validation
- **`app/services/`**: Business logic layer - contains service classes
- **`app/db/`**: Database connection management
  - Individual files for each database (postgres, mysql, mongodb, redis, cassandra, cockroachdb)
- **`app/utils/`**: Utility functions and helpers
  - `performance_monitor.py`: Real-time performance metrics collection
- **`app/core/`**: Core application configuration
  - `exceptions.py`: Custom exception classes

#### Benchmarks (`benchmarks/`)
- Performance testing implementations for each database
- `base.py`: Abstract base class for all benchmarks
- Individual benchmark files for each database type

#### Telemetry (`telemetry/`)
- Observability and monitoring setup
- `tracing.py`: OpenTelemetry distributed tracing
- `metrics.py`: Metrics collection and reporting

#### Configuration (`conf/`)
- `config.yaml`: YAML configuration file for experiment settings

#### Tests (`tests/`)
- Test suite organized to mirror application structure
- `conftest.py`: Pytest fixtures and test configuration
- `test_api/`: API endpoint tests
- `test_services/`: Service layer tests

#### Scripts (`scripts/`)
- Utility scripts for database setup and initialization
- `setup_db.py`: Database initialization script
- `init_cassandra.py`: Cassandra keyspace creation script

### Architecture Overview

- **API Layer** (`app/api/`): Handles HTTP requests and responses, routes to appropriate endpoints
- **Service Layer** (`app/services/`): Contains business logic and orchestrates operations
- **Model Layer** (`app/models/`): Database models using SQLAlchemy ORM
- **Schema Layer** (`app/schemas/`): Pydantic models for request/response validation
- **Database Layer** (`app/db/`): Database connection management for different data stores
- **Benchmarks** (`benchmarks/`): Performance testing implementations for each database
- **Telemetry** (`telemetry/`): Observability and monitoring setup
- **Tests** (`tests/`): Test suite organized to mirror application structure

## Error Handling

OptiStack provides comprehensive error handling with custom exceptions:

- **DatabaseConnectionError**: Database connection failures
- **ExperimentNotFoundError**: Experiment not found (404)
- **ExperimentExecutionError**: Errors during benchmark execution
- **InvalidDatabaseTypeError**: Unsupported database type
- **BenchmarkError**: Benchmark-specific errors

All errors are logged and returned with appropriate HTTP status codes and error messages.

## Roadmap

- [x] PostgreSQL benchmark module (enhanced with window functions, JSON, full-text search)
- [x] MySQL benchmark module
- [x] CockroachDB benchmark module
- [x] MongoDB benchmark module (enhanced with $lookup joins, text search)
- [x] Redis benchmark module (enhanced with sorted sets)
- [x] Cassandra benchmark module (enhanced with consistency levels, time-series)
- [x] InfluxDB benchmark module (time-series database)
- [x] Elasticsearch benchmark module (search and analytics)
- [ ] DynamoDB benchmark module (requires AWS credentials)
- [ ] Add load-testing suite (k6)
- [ ] Add CPU/Memory flamegraph generation
- [ ] Add WebSocket-based live metrics streaming
- [ ] Build frontend dashboard (React)
- [ ] Advanced analysis and comparison features

## Performance Metrics

Each experiment collects comprehensive performance metrics:

- **Duration**: Total execution time
- **Throughput**: Operations per second
- **Latency**: Query execution times with percentiles (P50, P95, P99)
- **CPU Usage**: Average and peak CPU utilization
- **Memory Usage**: Average and peak memory consumption

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database containers are running: `docker-compose ps`
   - Check environment variables in `.env` file
   - Ensure database credentials are correct

2. **Experiment Fails**
   - Check experiment status and results for error details
   - Verify database is accessible and healthy
   - Review logs for detailed error information

3. **Slow Performance**
   - Reduce `rows` in experiment config for faster tests
   - Check system resources (CPU, memory)
   - Verify database connection pooling settings

### Logs

Application logs are output to stdout. Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Contributing

Contributions are welcome! Please feel free to submit bug reports, feature requests, or pull requests on the GitHub repository.

For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License
