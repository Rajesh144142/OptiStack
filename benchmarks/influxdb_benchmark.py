from benchmarks.base import BaseBenchmark
from app.db.influxdb import get_influxdb_connection
from influxdb_client import Point, WritePrecision
from typing import Dict, Any
import time
from datetime import datetime, timedelta
import asyncio

class InfluxDBBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__()
        self.bucket = "optistack"
        self.measurement = "benchmark_test"
        
    async def setup(self, config: Dict[str, Any]) -> None:
        def _setup():
            with get_influxdb_connection() as client:
                bucket_api = client.buckets_api()
                try:
                    bucket = bucket_api.find_bucket_by_name(self.bucket)
                    if not bucket:
                        org_api = client.organizations_api()
                        org = org_api.find_organizations()[0]
                        bucket_api.create_bucket(bucket_name=self.bucket, org_id=org.id)
                except Exception:
                    pass
        await asyncio.to_thread(_setup)
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        num_rows = config.get("rows", 1000)
        operations = config.get("operations", ["write", "query"])
        
        results = {}
        
        if "write" in operations:
            write_result = await self._run_write_benchmark(num_rows)
            results["write"] = write_result
            
        if "query" in operations:
            query_result = await self._run_query_benchmark(num_rows)
            results["query"] = query_result
            
        if "aggregate" in operations:
            aggregate_result = await self._run_aggregate_benchmark()
            results["aggregate"] = aggregate_result
        
        return results
    
    async def _run_write_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _write():
            with get_influxdb_connection() as client:
                write_api = client.write_api(write_options=WritePrecision.NS)
                start = time.perf_counter()
                points = []
                for i in range(num_rows):
                    point = Point(self.measurement) \
                        .tag("sensor_id", f"sensor_{i % 10}") \
                        .field("temperature", 20.0 + (i % 50)) \
                        .field("humidity", 50.0 + (i % 30)) \
                        .field("pressure", 1013.25 + (i % 10)) \
                        .time(datetime.utcnow() - timedelta(seconds=num_rows-i))
                    points.append(point)
                write_api.write(bucket=self.bucket, record=points)
                write_api.close()
                elapsed = time.perf_counter() - start
                self._record_query_time(elapsed)
                return {
                    "points_written": num_rows,
                    "time_seconds": round(elapsed, 3),
                    "points_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
                }
        return await asyncio.to_thread(_write)
    
    async def _run_query_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _query():
            with get_influxdb_connection() as client:
                query_api = client.query_api()
                query_times = []
                queries = [
                    f'from(bucket:"{self.bucket}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "{self.measurement}") |> limit(n: 100)',
                    f'from(bucket:"{self.bucket}") |> range(start: -1h) |> filter(fn: (r) => r.sensor_id == "sensor_1") |> limit(n: 50)',
                    f'from(bucket:"{self.bucket}") |> range(start: -1h) |> filter(fn: (r) => r._field == "temperature" and r._value > 30) |> limit(n: 50)'
                ]
                for query in queries:
                    start = time.perf_counter()
                    result = query_api.query(query)
                    list(result)
                    elapsed = time.perf_counter() - start
                    query_times.append(elapsed)
                    self._record_query_time(elapsed)
                return {
                    "queries_executed": len(query_times),
                    "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
                    "min_time_seconds": round(min(query_times), 4) if query_times else 0,
                    "max_time_seconds": round(max(query_times), 4) if query_times else 0
                }
        return await asyncio.to_thread(_query)
    
    async def _run_aggregate_benchmark(self) -> Dict[str, Any]:
        def _aggregate():
            with get_influxdb_connection() as client:
                query_api = client.query_api()
                query = f'''
                from(bucket:"{self.bucket}")
                  |> range(start: -1h)
                  |> filter(fn: (r) => r._measurement == "{self.measurement}")
                  |> filter(fn: (r) => r._field == "temperature")
                  |> group()
                  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
                  |> limit(n: 100)
                '''
                start = time.perf_counter()
                result = query_api.query(query)
                list(result)
                elapsed = time.perf_counter() - start
                self._record_query_time(elapsed)
                return {
                    "time_seconds": round(elapsed, 3)
                }
        return await asyncio.to_thread(_aggregate)
    
    async def teardown(self) -> None:
        def _teardown():
            with get_influxdb_connection() as client:
                delete_api = client.delete_api()
                start = datetime.utcnow() - timedelta(days=1)
                stop = datetime.utcnow()
                try:
                    delete_api.delete(start, stop, f'_measurement="{self.measurement}"', bucket=self.bucket)
                except Exception:
                    pass
        await asyncio.to_thread(_teardown)
