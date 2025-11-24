# Docker Guide for OptiStack

## What is Docker?

Docker packages your application and its dependencies into containers that run the same way on any machine. Think of it as a lightweight virtual machine.

## Prerequisites

- Docker Desktop installed and running
- Make sure Docker Desktop is started (you'll see a Docker icon in your system tray)

## Quick Start

### Step 1: Start All Services

Open your terminal in the project directory and run:

```bash
docker-compose up
```

This will:
- Build your OptiStack application
- Start PostgreSQL, MySQL, MongoDB, Redis, Cassandra, and CockroachDB databases
- Make everything available on your local machine

### Step 2: Access Your Application

Once everything is running, your API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 3: Stop Services

Press `Ctrl + C` in the terminal, then run:

```bash
docker-compose down
```

## Common Docker Commands

### Start Services in Background (Detached Mode)

```bash
docker-compose up -d
```

### View Running Containers

```bash
docker-compose ps
```

### View Logs

```bash
docker-compose logs
```

View logs for a specific service:
```bash
docker-compose logs app
docker-compose logs postgres
```

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove All Data (Volumes)

```bash
docker-compose down -v
```

### Rebuild After Code Changes

```bash
docker-compose up --build
```

### Restart a Specific Service

```bash
docker-compose restart app
```

## Connecting to Databases

### PostgreSQL (using pgAdmin)

1. Open pgAdmin
2. Create a new server connection:
   - **Host**: `localhost`
   - **Port**: `5432`
   - **Username**: `postgres`
   - **Password**: `postgres`
   - **Database**: `optistack`

### MongoDB (using MongoDB Compass)

1. Open MongoDB Compass
2. Connect to: `mongodb://localhost:27017`
3. No authentication needed (default setup)

### MySQL

You can use any MySQL client:
- **Host**: `localhost`
- **Port**: `3307` (changed from 3306 to avoid conflicts)
- **Username**: `root`
- **Password**: `root`
- **Database**: `optistack`

### Redis

You can use Redis CLI or any Redis client:
- **Host**: `localhost`
- **Port**: `6379`

### Cassandra

You can use cqlsh (Cassandra Query Language Shell) or any Cassandra client:
- **Host**: `localhost`
- **Port**: `9042`
- **Keyspace**: `optistack` (create it first using the init script)

To initialize Cassandra keyspace:
```bash
docker-compose exec app python scripts/init_cassandra.py
```

### CockroachDB

CockroachDB uses PostgreSQL protocol. You can connect using:
- **Host**: `localhost`
- **Port**: `26257`
- **Username**: `root`
- **Password**: (empty, no password)
- **Database**: `optistack`

CockroachDB also provides a web UI at: http://localhost:8080

## Understanding docker-compose.yml

Your `docker-compose.yml` defines 7 services:

1. **app** - Your OptiStack FastAPI application
2. **postgres** - PostgreSQL database
3. **mysql** - MySQL database
4. **mongodb** - MongoDB database
5. **redis** - Redis cache
6. **cassandra** - Apache Cassandra database
7. **cockroachdb** - CockroachDB database

Each service runs in its own container, but they can communicate with each other.

## Troubleshooting

### Port Already in Use

If you get "port already in use" error:
- Stop any local database services running on ports 5432, 3307, 27017, 6379, 9042, 26257
- Or change the port mappings in `docker-compose.yml`

### Container Won't Start

```bash
docker-compose logs [service-name]
```

### Reset Everything

```bash
docker-compose down -v
docker-compose up --build
```

### Check Docker Desktop

- Open Docker Desktop
- Go to "Containers" tab to see running containers
- Check logs and resource usage

## Development Workflow

### Option 1: Run Everything with Docker

```bash
docker-compose up
```

### Option 2: Run Only Databases with Docker

1. Comment out the `app` service in `docker-compose.yml`
2. Run: `docker-compose up`
3. Run your app locally: `uvicorn app.main:app --reload`

This is useful for faster development since code changes don't require rebuilding the Docker image.

## Useful Tips

- **View logs in real-time**: `docker-compose logs -f`
- **Execute commands in a container**: `docker-compose exec app bash`
- **Check container status**: `docker ps`
- **Remove unused images**: `docker system prune`

## Next Steps

1. Start Docker Desktop
2. Run `docker-compose up` in your project directory
3. Open http://localhost:8000/docs to see your API
4. Connect pgAdmin and MongoDB Compass to the databases

