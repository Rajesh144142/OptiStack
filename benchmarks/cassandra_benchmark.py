from benchmarks.base import BaseBenchmark
from app.db.cassandra import get_cassandra_connection
from cassandra.query import SimpleStatement, ConsistencyLevel
from typing import Dict, Any
import time
import asyncio

class CassandraBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__()
        self.table_name = "benchmark_test"
        
    async def setup(self, config: Dict[str, Any]) -> None:
        def _setup():
            with get_cassandra_connection() as session:
                session.execute(f"""
                    DROP TABLE IF EXISTS {self.table_name}
                """)
                session.execute(f"""
                    CREATE TABLE {self.table_name} (
                        id INT PRIMARY KEY,
                        name TEXT,
                        email TEXT,
                        age INT,
                        score INT,
                        created_at TIMESTAMP
                    )
                """)
        await asyncio.to_thread(_setup)
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        num_rows = config.get("rows", 1000)
        operations = config.get("operations", ["insert", "select"])
        
        results = {}
        
        if "insert" in operations:
            insert_result = await self._run_insert_benchmark(num_rows)
            results["insert"] = insert_result
            
        if "select" in operations:
            select_result = await self._run_select_benchmark(num_rows)
            results["select"] = select_result
            
        if "update" in operations:
            update_result = await self._run_update_benchmark(num_rows)
            results["update"] = update_result
            
        if "consistency" in operations:
            consistency_result = await self._run_consistency_benchmark(num_rows)
            results["consistency"] = consistency_result
            
        if "timeseries" in operations:
            timeseries_result = await self._run_timeseries_benchmark(num_rows)
            results["timeseries"] = timeseries_result
        
        return results
    
    async def _run_insert_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _insert():
            data = self.generate_test_data(num_rows)
            with get_cassandra_connection() as session:
                insert_stmt = session.prepare(f"""
                    INSERT INTO {self.table_name} (id, name, email, age, score, created_at)
                    VALUES (?, ?, ?, ?, ?, toTimestamp(now()))
                """)
                
                start = time.perf_counter()
                for row in data:
                    session.execute(insert_stmt, (
                        row["id"],
                        row["name"],
                        row["email"],
                        row["age"],
                        row["score"]
                    ))
                elapsed = time.perf_counter() - start
                self._record_query_time(elapsed)
                return {
                    "rows_inserted": num_rows,
                    "time_seconds": round(elapsed, 3),
                    "rows_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
                }
        return await asyncio.to_thread(_insert)
    
    async def _run_select_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _select():
            query_times = []
            samples = min(100, num_rows // 10)
            with get_cassandra_connection() as session:
                select_stmt = session.prepare(f"""
                    SELECT * FROM {self.table_name} WHERE id = ?
                """)
                for i in range(samples):
                    start = time.perf_counter()
                    session.execute(select_stmt, (i,))
                    elapsed = time.perf_counter() - start
                    query_times.append(elapsed)
                    self._record_query_time(elapsed)
            return {
                "queries_executed": len(query_times),
                "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
                "min_time_seconds": round(min(query_times), 4) if query_times else 0,
                "max_time_seconds": round(max(query_times), 4) if query_times else 0
            }
        return await asyncio.to_thread(_select)
    
    async def _run_update_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _update():
            updates = min(100, num_rows // 10)
            query_times = []
            with get_cassandra_connection() as session:
                update_stmt = session.prepare(f"""
                    UPDATE {self.table_name}
                    SET score = score + 1
                    WHERE id = ?
                """)
                for i in range(updates):
                    start = time.perf_counter()
                    session.execute(update_stmt, (i,))
                    elapsed = time.perf_counter() - start
                    query_times.append(elapsed)
                    self._record_query_time(elapsed)
            return {
                "rows_updated": updates,
                "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
            }
        return await asyncio.to_thread(_update)
    
    async def _run_consistency_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _consistency():
            query_times = []
            consistency_levels = [ConsistencyLevel.ONE, ConsistencyLevel.QUORUM, ConsistencyLevel.ALL]
            with get_cassandra_connection() as session:
                select_stmt = session.prepare(f"""
                    SELECT * FROM {self.table_name} WHERE id = ?
                """)
                for consistency in consistency_levels:
                    select_stmt.consistency_level = consistency
                    for i in range(min(20, num_rows // 50)):
                        start = time.perf_counter()
                        session.execute(select_stmt, (i,))
                        elapsed = time.perf_counter() - start
                        query_times.append(elapsed)
                        self._record_query_time(elapsed)
            return {
                "queries_executed": len(query_times),
                "consistency_levels_tested": len(consistency_levels),
                "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
            }
        return await asyncio.to_thread(_consistency)
    
    async def _run_timeseries_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _timeseries():
            timeseries_table = f"{self.table_name}_timeseries"
            with get_cassandra_connection() as session:
                session.execute(f"""
                    DROP TABLE IF EXISTS {timeseries_table}
                """)
                session.execute(f"""
                    CREATE TABLE {timeseries_table} (
                        sensor_id INT,
                        timestamp TIMESTAMP,
                        value DOUBLE,
                        PRIMARY KEY (sensor_id, timestamp)
                    ) WITH CLUSTERING ORDER BY (timestamp DESC)
                """)
                insert_stmt = session.prepare(f"""
                    INSERT INTO {timeseries_table} (sensor_id, timestamp, value)
                    VALUES (?, toTimestamp(now()), ?)
                """)
                start = time.perf_counter()
                for i in range(min(num_rows, 1000)):
                    session.execute(insert_stmt, (i % 10, float(i * 1.5)))
                elapsed = time.perf_counter() - start
                self._record_query_time(elapsed)
                query_times = []
                select_stmt = session.prepare(f"""
                    SELECT * FROM {timeseries_table}
                    WHERE sensor_id = ? AND timestamp > ?
                    LIMIT 100
                """)
                for sensor_id in range(5):
                    start = time.perf_counter()
                    from datetime import datetime, timedelta
                    from cassandra.util import datetime_from_timestamp
                    time_threshold = datetime_from_timestamp(time.time() - 3600)
                    session.execute(select_stmt, (sensor_id, time_threshold))
                    elapsed = time.perf_counter() - start
                    query_times.append(elapsed)
                    self._record_query_time(elapsed)
                session.execute(f"DROP TABLE IF EXISTS {timeseries_table}")
            return {
                "data_points_inserted": min(num_rows, 1000),
                "insert_time_seconds": round(elapsed, 3),
                "queries_executed": len(query_times),
                "avg_query_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
            }
        return await asyncio.to_thread(_timeseries)
    
    async def teardown(self) -> None:
        def _teardown():
            with get_cassandra_connection() as session:
                session.execute(f"DROP TABLE IF EXISTS {self.table_name}")
                session.execute(f"DROP TABLE IF EXISTS {self.table_name}_timeseries")
        await asyncio.to_thread(_teardown)
