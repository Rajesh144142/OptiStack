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

### Prerequisites

- Python 3.8 or higher
- pip
- Docker (optional, for containerized deployment)

### Installation

```bash
git clone https://github.com/Rajesh144142/OptiStack.git
cd OptiStack
pip install -r requirements.txt
```

### Running the Project

To run the project locally:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Deployment

Build the Docker image:

```bash
docker build -t optistack:latest .
```

Run the Docker container:

```bash
docker run -p 8000:8000 optistack:latest
```

## Configuration

You can configure various aspects of the experiment, such as:
- Number of rows to process
- Concurrent queries
- Data store connection settings
- Experiment parameters

Configuration files are located in the `conf` directory.

## Project Structure

```
OptiStack/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── db/
│   └── main.py
├── benchmarks/
├── telemetry/
├── conf/
├── README.md
└── requirements.txt
```

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
