# OptiStack Testing Guide

## What We're Doing

OptiStack is a **database performance benchmarking tool** that helps you:

1. **Test Performance**: Run standardized performance tests against different databases
2. **Measure Metrics**: Collect detailed metrics (speed, CPU, memory, latency)
3. **Compare Results**: Compare different databases side-by-side to make informed decisions
4. **Identify Bottlenecks**: Understand which database performs best for your specific workload

### How It Works

1. **Create Experiment**: Define which database to test, how many rows, and which operations
2. **Run Benchmark**: OptiStack executes the operations and measures performance
3. **Collect Metrics**: System automatically tracks CPU, memory, latency during execution
4. **Get Results**: Receive comprehensive performance data for analysis

---

## Supported Databases & Tests

### 1. PostgreSQL (Relational SQL Database)

**What It Tests**: ACID-compliant relational database with advanced features

**Available Operations**:
- `insert` - Insert rows into tables
- `select` - Query data with various filters
- `update` - Update existing records
- `join` - Test JOIN operations between tables
- `window` - Window functions (ROW_NUMBER, LAG, LEAD, running sums)
- `json` - JSONB queries and operations
- `fulltext` - Full-text search with GIN indexes

**API Payload Example**:
```json
{
  "name": "PostgreSQL Complex Query Test",
  "database_type": "postgres",
  "config": {
    "rows": 10000,
    "operations": ["insert", "select", "join", "window", "json", "fulltext"]
  }
}
```

**Expected Results**:
- **Insert**: 3,000-5,000 rows/second
- **Select**: 0.5-2ms average latency
- **Join**: 5-20ms for multi-table joins
- **Window Functions**: 10-50ms depending on complexity
- **JSON Queries**: 1-5ms for JSONB operations
- **Full-text Search**: 5-30ms with GIN indexes

**Best For**: Complex queries, transactions, analytics, JSON data, full-text search

---

### 2. MySQL (Relational SQL Database)

**What It Tests**: Popular relational database optimized for web applications

**Available Operations**:
- `insert` - Insert rows into tables
- `select` - Query data with various filters
- `update` - Update existing records
- `join` - Test JOIN operations between tables

**API Payload Example**:
```json
{
  "name": "MySQL Web App Test",
  "database_type": "mysql",
  "config": {
    "rows": 5000,
    "operations": ["insert", "select", "update", "join"]
  }
}
```

**Expected Results**:
- **Insert**: 2,000-4,000 rows/second
- **Select**: 0.3-1.5ms average latency
- **Update**: 1-3ms per update
- **Join**: 3-15ms for multi-table joins

**Best For**: Web applications, read-heavy workloads, simple to moderate queries

---

### 3. CockroachDB (Distributed SQL Database)

**What It Tests**: Distributed SQL database with global ACID transactions

**Available Operations**:
- `insert` - Insert rows into tables
- `select` - Query data with various filters
- `update` - Update existing records
- `join` - Test JOIN operations
- `transaction` - Distributed transaction performance

**API Payload Example**:
```json
{
  "name": "CockroachDB Distributed Test",
  "database_type": "cockroachdb",
  "config": {
    "rows": 5000,
    "operations": ["insert", "select", "transaction"]
  }
}
```

**Expected Results**:
- **Insert**: 1,500-3,000 rows/second (network overhead)
- **Select**: 1-5ms average latency (cross-region may be higher)
- **Transaction**: 10-50ms for distributed transactions
- **Join**: 5-25ms (distributed query overhead)

**Best For**: Multi-region applications, distributed systems, global ACID transactions

---

### 4. MongoDB (Document Database)

**What It Tests**: Flexible document database with schema-less design

**Available Operations**:
- `insert` - Insert documents into collections
- `select` - Query documents with filters
- `update` - Update existing documents
- `aggregate` - Aggregation pipeline operations
- `lookup` - $lookup joins between collections
- `textsearch` - Full-text search queries

**API Payload Example**:
```json
{
  "name": "MongoDB Document Operations",
  "database_type": "mongodb",
  "config": {
    "rows": 10000,
    "operations": ["insert", "select", "aggregate", "lookup", "textsearch"]
  }
}
```

**Expected Results**:
- **Insert**: 2,000-5,000 documents/second
- **Select**: 0.5-3ms average latency
- **Aggregate**: 5-50ms depending on pipeline complexity
- **Lookup**: 10-100ms for collection joins
- **Text Search**: 5-30ms with text indexes

**Best For**: Rapid development, nested data, flexible schemas, content management

---

### 5. Redis (In-Memory Key-Value Store)

**What It Tests**: Fastest database for caching and real-time data

**Available Operations**:
- `set` - Set key-value pairs
- `get` - Retrieve values by key
- `pipeline` - Batch operations for better throughput
- `hash` - Hash data structure operations
- `sortedset` - Sorted sets for leaderboards and range queries

**API Payload Example**:
```json
{
  "name": "Redis Cache Performance",
  "database_type": "redis",
  "config": {
    "rows": 50000,
    "operations": ["set", "get", "pipeline", "hash", "sortedset"]
  }
}
```

**Expected Results**:
- **Set**: 10,000-50,000 operations/second
- **Get**: 0.1-1ms average latency (sub-millisecond)
- **Pipeline**: 50,000-200,000 operations/second
- **Hash**: 5,000-20,000 operations/second
- **Sorted Set**: 2,000-10,000 operations/second

**Best For**: Caching, session storage, real-time data, leaderboards, pub/sub

---

### 6. Cassandra (Wide-Column Database)

**What It Tests**: High write throughput database for global scale

**Available Operations**:
- `insert` - Insert rows with partition keys
- `select` - Query by partition key (required)
- `update` - Update existing rows
- `consistency` - Test different consistency levels (ONE, QUORUM, ALL)
- `timeseries` - Time-series data patterns with clustering keys

**API Payload Example**:
```json
{
  "name": "Cassandra Write Throughput",
  "database_type": "cassandra",
  "config": {
    "rows": 20000,
    "operations": ["insert", "select", "consistency", "timeseries"]
  }
}
```

**Expected Results**:
- **Insert**: 5,000-15,000 rows/second (very high write throughput)
- **Select**: 1-5ms (requires partition key)
- **Consistency ONE**: Fastest (1-3ms)
- **Consistency QUORUM**: Slower (5-15ms)
- **Consistency ALL**: Slowest (10-30ms)
- **Time-series**: 3,000-10,000 writes/second

**Best For**: Time-series data, high write loads, global scale, eventual consistency

---

### 7. InfluxDB (Time-Series Database)

**What It Tests**: Optimized database for time-stamped metrics and IoT data

**Available Operations**:
- `write` - Write time-series data points
- `query` - Query time-series data with Flux
- `aggregate` - Aggregate operations on time-series data

**API Payload Example**:
```json
{
  "name": "InfluxDB Time-Series Test",
  "database_type": "influxdb",
  "config": {
    "rows": 50000,
    "operations": ["write", "query", "aggregate"]
  }
}
```

**Expected Results**:
- **Write**: 10,000-50,000 points/second
- **Query**: 5-50ms depending on time range
- **Aggregate**: 10-100ms for complex aggregations

**Best For**: Metrics, IoT data, monitoring dashboards, time-stamped measurements

---

### 8. Elasticsearch (Search & Analytics Engine)

**What It Tests**: Full-text search and complex analytics

**Available Operations**:
- `index` - Index documents for search
- `search` - Search queries
- `aggregate` - Aggregation operations
- `fulltext` - Full-text search queries

**API Payload Example**:
```json
{
  "name": "Elasticsearch Search Test",
  "database_type": "elasticsearch",
  "config": {
    "rows": 10000,
    "operations": ["index", "search", "aggregate", "fulltext"]
  }
}
```

**Expected Results**:
- **Index**: 1,000-5,000 documents/second
- **Search**: 5-50ms depending on query complexity
- **Aggregate**: 10-200ms for complex aggregations
- **Full-text Search**: 10-100ms with relevance scoring

**Best For**: Search functionality, log analysis, data exploration, complex queries

---

## How to Make Comparisons

### Step 1: Create Similar Experiments

Run the **same workload** on different databases for fair comparison:

**Example: Insert Performance Comparison**

```bash
# PostgreSQL
curl.exe -X POST http://localhost:8000/api/v1/experiments/ \
  -H "Content-Type: application/json" \
  -d '{"name":"PostgreSQL Insert","database_type":"postgres","config":{"rows":10000,"operations":["insert"]}}'

# MongoDB
curl.exe -X POST http://localhost:8000/api/v1/experiments/ \
  -H "Content-Type: application/json" \
  -d '{"name":"MongoDB Insert","database_type":"mongodb","config":{"rows":10000,"operations":["insert"]}}'

# Redis
curl.exe -X POST http://localhost:8000/api/v1/experiments/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Redis Insert","database_type":"redis","config":{"rows":10000,"operations":["set"]}}'
```

### Step 2: Run All Experiments

```bash
# Run each experiment (use the IDs from step 1)
curl.exe -X POST http://localhost:8000/api/v1/experiments/{experiment_id}/run
```

### Step 3: Get Results and Compare

```bash
# Get all experiments
curl.exe http://localhost:8000/api/v1/experiments/

# Get specific experiment
curl.exe http://localhost:8000/api/v1/experiments/{experiment_id}
```

### Step 4: Compare Key Metrics

Compare these metrics across databases:

| Metric | What It Means | How to Compare |
|--------|---------------|----------------|
| **ops_per_second** | Operations per second | Higher is better |
| **latency_ms.avg** | Average response time | Lower is better |
| **latency_ms.p95** | 95th percentile latency | Lower is better (shows worst-case) |
| **latency_ms.p99** | 99th percentile latency | Lower is better (shows outliers) |
| **cpu_percent.avg** | Average CPU usage | Lower is better (more efficient) |
| **memory_mb.avg** | Average memory usage | Lower is better (more efficient) |
| **duration_seconds** | Total execution time | Lower is better |

### Example Comparison Table

| Database | Ops/sec | Avg Latency | P95 Latency | CPU % | Memory MB |
|----------|---------|-------------|-------------|-------|-----------|
| Redis | 50,000 | 0.5ms | 1.2ms | 85% | 120 |
| PostgreSQL | 4,000 | 2.5ms | 8.5ms | 60% | 150 |
| MongoDB | 3,500 | 3.2ms | 12.1ms | 55% | 180 |

**Analysis**: Redis is fastest but uses more CPU. PostgreSQL is balanced. MongoDB uses more memory.

---

## Complete Workflow Example

### PowerShell Script for Comparison

```powershell
# Create experiments for comparison
$databases = @("postgres", "mongodb", "redis")
$experimentIds = @()

foreach ($db in $databases) {
    $body = @{
        name = "$db Insert Test"
        database_type = $db
        config = @{
            rows = 10000
            operations = if ($db -eq "redis") { @("set") } else { @("insert") }
        }
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/experiments/" `
        -Method POST -ContentType "application/json" -Body $body
    
    $experimentIds += $result.id
    Write-Host "Created $db experiment: $($result.id)"
}

# Run all experiments
foreach ($id in $experimentIds) {
    Write-Host "Running experiment: $id"
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/experiments/$id/run" -Method POST | Out-Null
}

# Wait for completion
Write-Host "Waiting 15 seconds for experiments to complete..."
Start-Sleep -Seconds 15

# Get and display results
Write-Host "`n=== COMPARISON RESULTS ===" -ForegroundColor Green
foreach ($id in $experimentIds) {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/experiments/$id"
    Write-Host "`n$($result.name) ($($result.database_type))" -ForegroundColor Cyan
    Write-Host "  Status: $($result.status)"
    if ($result.results) {
        $metrics = $result.results.performance_metrics
        Write-Host "  Ops/sec: $($metrics.ops_per_second)"
        Write-Host "  Avg Latency: $($metrics.latency_ms.avg)ms"
        Write-Host "  P95 Latency: $($metrics.latency_ms.p95)ms"
        Write-Host "  CPU: $($metrics.cpu_percent.avg)%"
        Write-Host "  Memory: $($metrics.memory_mb.avg)MB"
    }
}
```

---

## Understanding Results

### Benchmark Results Structure

```json
{
  "benchmark_results": {
    "insert": {
      "rows_inserted": 10000,
      "time_seconds": 2.5,
      "rows_per_second": 4000
    }
  },
  "performance_metrics": {
    "duration_seconds": 2.8,
    "total_queries": 10001,
    "ops_per_second": 3571.43,
    "latency_ms": {
      "avg": 2.5,
      "p50": 1.8,
      "p95": 8.5,
      "p99": 15.2
    },
    "cpu_percent": {
      "avg": 65.3,
      "max": 85.2
    },
    "memory_mb": {
      "avg": 145.8,
      "max": 156.2
    }
  }
}
```

### What Each Metric Means

- **rows_per_second**: Throughput specific to the operation
- **ops_per_second**: Overall operations per second (includes all operations)
- **latency_ms.avg**: Average response time (typical performance)
- **latency_ms.p50**: Median response time (50% of requests)
- **latency_ms.p95**: 95th percentile (95% of requests are faster)
- **latency_ms.p99**: 99th percentile (99% of requests are faster)
- **cpu_percent**: CPU utilization (higher = more CPU intensive)
- **memory_mb**: Memory consumption (higher = uses more RAM)

---

## Best Practices

### 1. Use Similar Workloads
- Same number of rows
- Same operations
- Same data patterns

### 2. Run Multiple Times
- Database performance can vary
- Run 3-5 times and average results
- Account for system load

### 3. Test Realistic Scenarios
- Use row counts similar to your production data
- Test operations you'll actually use
- Consider concurrent users

### 4. Compare Fairly
- Don't compare Redis (in-memory) with PostgreSQL (disk-based) for raw speed
- Compare databases with similar use cases
- Consider consistency guarantees (ACID vs eventual)

### 5. Look at Multiple Metrics
- Don't just look at speed
- Consider CPU, memory, latency percentiles
- Balance performance vs resource usage

---

## Common Test Scenarios

### Scenario 1: Web Application Backend
**Databases**: PostgreSQL, MySQL, MongoDB
**Operations**: `["insert", "select", "update"]`
**Rows**: 10,000-50,000
**Focus**: Balanced read/write performance

### Scenario 2: Caching Layer
**Databases**: Redis
**Operations**: `["set", "get", "pipeline"]`
**Rows**: 100,000+
**Focus**: Ultra-low latency, high throughput

### Scenario 3: Analytics & Reporting
**Databases**: PostgreSQL, Elasticsearch
**Operations**: `["select", "join", "aggregate"]` or `["search", "aggregate"]`
**Rows**: 100,000+
**Focus**: Complex query performance

### Scenario 4: Time-Series Data
**Databases**: InfluxDB, Cassandra
**Operations**: `["write", "query"]` or `["insert", "timeseries"]`
**Rows**: 1,000,000+
**Focus**: High write throughput, time-range queries

### Scenario 5: Full-Text Search
**Databases**: PostgreSQL, Elasticsearch, MongoDB
**Operations**: `["fulltext"]` or `["textsearch"]` or `["search"]`
**Rows**: 50,000+
**Focus**: Search relevance and speed

---

## Troubleshooting

### Experiment Fails
- Check database is running: `docker-compose ps`
- Verify database connection in logs
- Check experiment status for error details

### Slow Performance
- Reduce `rows` count for faster tests
- Check system resources (CPU, memory)
- Verify database is not under heavy load

### Inconsistent Results
- Run experiments multiple times
- Ensure no other processes are using resources
- Use similar system conditions

---

## Next Steps

1. **Start Simple**: Test one database with basic operations
2. **Compare**: Run same test on 2-3 databases
3. **Analyze**: Compare metrics and identify best fit
4. **Optimize**: Test with different row counts and operations
5. **Document**: Keep notes on which database works best for your use case

---

## Quick Reference: All Operations by Database

| Database | Available Operations |
|----------|---------------------|
| **PostgreSQL** | `insert`, `select`, `update`, `join`, `window`, `json`, `fulltext` |
| **MySQL** | `insert`, `select`, `update`, `join` |
| **CockroachDB** | `insert`, `select`, `update`, `join`, `transaction` |
| **MongoDB** | `insert`, `select`, `update`, `aggregate`, `lookup`, `textsearch` |
| **Redis** | `set`, `get`, `pipeline`, `hash`, `sortedset` |
| **Cassandra** | `insert`, `select`, `update`, `consistency`, `timeseries` |
| **InfluxDB** | `write`, `query`, `aggregate` |
| **Elasticsearch** | `index`, `search`, `aggregate`, `fulltext` |

---

## Postman Collection

### Import Ready-to-Use Requests

We've created a **Postman Collection** file (`OptiStack_Postman_Collection.json`) that you can import directly into Postman!

### How to Import:

1. **Open Postman**
2. **Click "Import"** (top left)
3. **Select "Upload Files"**
4. **Choose** `OptiStack_Postman_Collection.json`
5. **Click "Import"**

### What's Included:

✅ **All 8 Databases** - Pre-configured requests for each database type
✅ **Common Scenarios** - Web app, caching, analytics, time-series, search
✅ **Experiment Management** - Create, run, and get results
✅ **Health Checks** - Verify API is running
✅ **Environment Variables** - Easy to switch between environments

### Using the Collection:

1. **Set Base URL**: 
   - Collection variables → `base_url` → Set to `http://localhost:8000`
   - Or create a Postman Environment with `base_url` variable

2. **Create Experiment**:
   - Go to any database folder (e.g., "PostgreSQL Tests")
   - Click "Send" on a "Create" request
   - Copy the `id` from response

3. **Run Experiment**:
   - Go to "Experiment Management" folder
   - Use "Run Experiment" request
   - Replace `{{experiment_id}}` with the ID from step 2
   - Click "Send"

4. **Get Results**:
   - Wait 5-15 seconds
   - Use "Get Experiment by ID" request
   - Replace `{{experiment_id}}` with your experiment ID
   - Click "Send" to see results

### Quick Tips:

- **Save IDs**: After creating an experiment, copy the `id` and set it as `experiment_id` variable for easy reuse
- **Compare Results**: Create similar experiments for different databases, then compare results side-by-side
- **Use Scenarios**: The "Comparison Scenarios" folder has pre-configured requests for common use cases

---

**Happy Benchmarking! 🚀**

