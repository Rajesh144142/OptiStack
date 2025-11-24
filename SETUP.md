# Setup Guide

## Quick Start (Using Docker)

### Prerequisites
- Docker Desktop installed and running

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OptiStack
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Initialize Cassandra keyspace** (one-time setup)
   ```bash
   docker-compose exec app sh -c "PYTHONPATH=/app python scripts/init_cassandra.py"
   ```

4. **Access the API**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- Docker Desktop (for databases only)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OptiStack
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start databases only**
   ```bash
   docker-compose up -d postgres mysql mongodb redis cassandra cockroachdb
   ```

6. **Initialize Cassandra keyspace**
   ```bash
   docker-compose exec app sh -c "PYTHONPATH=/app python scripts/init_cassandra.py"
   ```

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Connection Details

- **PostgreSQL**: `localhost:5432` (user: `postgres`, password: `postgres`, db: `optistack`)
- **MySQL**: `localhost:3307` (user: `root`, password: `root`, db: `optistack`)
- **MongoDB**: `mongodb://localhost:27017`
- **Redis**: `localhost:6379`
- **Cassandra**: `localhost:9042` (keyspace: `optistack`)
- **CockroachDB**: `localhost:26257` (user: `root`, password: none, db: `optistack`)
- **CockroachDB Web UI**: http://localhost:8080

## Common Commands

### Docker Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs

# View logs for specific service
docker-compose logs app

# Restart a service
docker-compose restart app

# Check service status
docker-compose ps
```

### Development Commands
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code
black .

# Lint code
flake8 app
```

## Troubleshooting

### Port conflicts
If you get "port already in use" errors:
- Stop local database services
- Or change port mappings in `docker-compose.yml`

### Container won't start
```bash
docker-compose logs <service-name>
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
```

