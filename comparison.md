# Database Comparison Guide

This document outlines key differences between databases supported by OptiStack to help design appropriate benchmarks for each.

## Data Models

| Database | Data Model | Schema | Primary Use Case |
|----------|-----------|--------|-----------------|
| **PostgreSQL** | Relational (ACID) | Fixed schema, tables with relationships | Complex queries, transactions, analytics |
| **MySQL** | Relational (ACID) | Fixed schema, tables with relationships | Web applications, read-heavy workloads |
| **CockroachDB** | Distributed SQL | Fixed schema, globally distributed | Multi-region applications, ACID at scale |
| **MongoDB** | Document store | Flexible schema, JSON documents | Rapid development, nested data, content management |
| **Cassandra** | Wide-column | Flexible schema, partition-based | Time-series, high write throughput, global scale |
| **Redis** | Key-value / Data structures | No schema, in-memory | Caching, session storage, real-time data |
| **DynamoDB** | Key-value / Document | Flexible schema, managed service | Serverless apps, auto-scaling workloads |

## Consistency Models

| Database | Consistency | Transactions | Trade-offs |
|----------|-------------|--------------|------------|
| **PostgreSQL** | Strong (ACID) | Full ACID, multi-table | Lower write throughput |
| **MySQL** | Strong (ACID) | Full ACID, configurable isolation | Replication lag possible |
| **CockroachDB** | Strong (ACID) | Distributed ACID | Network latency, transaction conflicts |
| **MongoDB** | Tunable | Single-document ACID, multi-document optional | Write concern affects performance |
| **Cassandra** | Tunable (AP) | No transactions | Eventual consistency, read repair overhead |
| **Redis** | Strong (single node) | Atomic operations, no multi-key transactions | Memory limits |
| **DynamoDB** | Tunable | Single-item ACID, optional transactions | Throttling under load |

## Performance Characteristics

### Write Performance
- **Highest**: Redis (in-memory), Cassandra (append-only, no updates)
- **High**: DynamoDB (managed, auto-scaling), MongoDB (bulk writes)
- **Medium**: PostgreSQL (ACID overhead), MySQL (depends on storage engine)
- **Lower**: CockroachDB (distributed consensus overhead)

### Read Performance
- **Highest**: Redis (in-memory, sub-millisecond)
- **High**: PostgreSQL (indexes, query optimizer), MySQL (query cache)
- **Medium**: MongoDB (indexes, aggregation), DynamoDB (single-item reads)
- **Lower**: Cassandra (eventual consistency, read repair), CockroachDB (cross-region latency)

### Query Complexity
- **Most Complex**: PostgreSQL (JOINs, window functions, CTEs, full-text search)
- **Complex**: MySQL (JOINs, subqueries), CockroachDB (distributed SQL)
- **Moderate**: MongoDB (aggregation pipelines, $lookup)
- **Simple**: Redis (key lookups, data structure operations)
- **Limited**: Cassandra (partition key required, no JOINs), DynamoDB (key-based, limited queries)

## Scalability Patterns

| Database | Scaling Strategy | Horizontal Scaling | Vertical Scaling |
|----------|------------------|-------------------|------------------|
| **PostgreSQL** | Read replicas, sharding (manual) | Limited (requires application logic) | Excellent |
| **MySQL** | Read replicas, sharding (manual) | Limited (requires application logic) | Excellent |
| **CockroachDB** | Automatic sharding, multi-region | Native, automatic | Good |
| **MongoDB** | Sharding, replica sets | Native, automatic | Good |
| **Cassandra** | Ring architecture, no master | Native, linear scaling | Limited |
| **Redis** | Cluster mode, sentinel | Native (with Redis Cluster) | Excellent |
| **DynamoDB** | Automatic partitioning | Managed, automatic | Managed |

## Data Access Patterns

### Best For Read-Heavy
1. **Redis** - Sub-millisecond reads, cache patterns
2. **PostgreSQL** - Complex analytical queries
3. **MySQL** - Simple queries with query cache

### Best For Write-Heavy
1. **Cassandra** - Append-only, high write throughput
2. **Redis** - In-memory writes
3. **DynamoDB** - Auto-scaling writes

### Best For Mixed Workloads
1. **PostgreSQL** - Balanced with good optimization
2. **MongoDB** - Flexible schema, good balance
3. **CockroachDB** - Distributed ACID transactions

## Benchmark Focus Areas

### PostgreSQL
- Complex JOIN performance (2-5 tables)
- Window function execution time
- Transaction throughput
- Index effectiveness (B-tree, GIN, GiST)
- Full-text search performance
- JSON query performance

### MySQL
- Read vs write performance
- Storage engine comparison (InnoDB vs MyISAM)
- Replication lag measurement
- Query cache effectiveness
- Connection pool efficiency

### CockroachDB
- Multi-region latency
- Distributed transaction performance
- Range split behavior
- Transaction conflict rates
- Cross-region query performance

### MongoDB
- Aggregation pipeline performance
- Index usage on nested fields
- Shard balancing impact
- Write concern performance trade-offs
- Document size impact on performance

### Cassandra
- Write throughput (append-only)
- Partition key distribution
- Consistency level impact (ONE vs QUORUM vs ALL)
- Read repair overhead
- Compaction impact on reads
- Time-series data patterns

### Redis
- Operations per second (OPS)
- Memory efficiency (data structures)
- Cache hit/miss ratios
- Pipeline vs individual operations
- Persistence overhead (RDB vs AOF)
- Eviction policy performance

### DynamoDB
- Provisioned vs on-demand throughput
- Hot partition detection
- Throttling behavior
- Global table replication latency
- Query vs Scan performance
- Consumed capacity units

## Operational Differences

### Setup Complexity
- **Easiest**: DynamoDB (managed), Redis (single node)
- **Easy**: MongoDB (single node), PostgreSQL (Docker)
- **Moderate**: MySQL, CockroachDB
- **Complex**: Cassandra (multi-node setup, tuning)

### Monitoring Requirements
- **PostgreSQL/MySQL**: Query performance, connection pools, slow query logs
- **MongoDB**: Replica set health, shard balancing, oplog lag
- **Cassandra**: Node health, compaction, read repair metrics
- **Redis**: Memory usage, eviction rates, hit ratios
- **DynamoDB**: Throttling, consumed capacity, partition metrics
- **CockroachDB**: Node status, range distribution, transaction conflicts

### Failure Handling
- **PostgreSQL/MySQL**: Failover to replicas, manual intervention
- **MongoDB**: Automatic failover (replica sets)
- **Cassandra**: No single point of failure, eventual consistency
- **Redis**: Sentinel for HA, cluster mode for sharding
- **DynamoDB**: Managed, automatic failover
- **CockroachDB**: Automatic rebalancing, multi-region failover

## Benchmark Design Implications

### What to Measure
1. **Latency**: P50, P95, P99 percentiles (not just averages)
2. **Throughput**: Operations per second under different loads
3. **Resource Usage**: CPU, memory, disk I/O, network
4. **Consistency**: Read-after-write guarantees, stale data detection
5. **Scalability**: Performance degradation with data/load growth

### What NOT to Compare Directly
- Don't compare raw OPS between Redis and PostgreSQL (different purposes)
- Don't compare JOIN performance between MongoDB and PostgreSQL (different models)
- Don't compare write throughput without considering consistency guarantees

### Fair Comparisons
- Similar operations: Bulk inserts, single-key lookups, range queries
- Similar consistency: Compare ACID databases together, AP databases together
- Similar use cases: Time-series (Cassandra vs InfluxDB), caching (Redis vs Memcached)

## Key Takeaways for OptiStack

1. **Each database excels in different scenarios** - benchmarks must reflect real-world usage
2. **Consistency vs Performance trade-off** - measure both dimensions
3. **Scalability patterns differ** - test horizontal vs vertical scaling separately
4. **Query capabilities vary** - design benchmarks that match each database's strengths
5. **Operational overhead matters** - include setup time, monitoring complexity in comparisons

