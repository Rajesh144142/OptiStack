from benchmarks.base import BaseBenchmark
from app.db.redis import get_redis_connection
from typing import Dict, Any
import time
import json

class RedisBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__()
        self.key_prefix = "benchmark:"
        
    async def setup(self, config: Dict[str, Any]) -> None:
        async with get_redis_connection() as client:
            keys = await client.keys(f"{self.key_prefix}*")
            if keys:
                await client.delete(*keys)
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        num_rows = config.get("rows", 1000)
        operations = config.get("operations", ["set", "get"])
        
        results = {}
        
        async with get_redis_connection() as client:
            if "set" in operations:
                set_result = await self._run_set_benchmark(client, num_rows)
                results["set"] = set_result
                
            if "get" in operations:
                get_result = await self._run_get_benchmark(client, num_rows)
                results["get"] = get_result
                
            if "pipeline" in operations:
                pipeline_result = await self._run_pipeline_benchmark(client, num_rows)
                results["pipeline"] = pipeline_result
                
            if "hash" in operations:
                hash_result = await self._run_hash_benchmark(client, num_rows)
                results["hash"] = hash_result
                
            if "sortedset" in operations:
                sortedset_result = await self._run_sorted_set_benchmark(client, num_rows)
                results["sortedset"] = sortedset_result
        
        return results
    
    async def _run_set_benchmark(self, client, num_rows: int) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows)
        
        start = time.perf_counter()
        
        for row in data:
            key = f"{self.key_prefix}string:{row['id']}"
            value = json.dumps(row)
            await client.set(key, value)
        
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "keys_set": num_rows,
            "time_seconds": round(elapsed, 3),
            "ops_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
        }
    
    async def _run_get_benchmark(self, client, num_rows: int) -> Dict[str, Any]:
        query_times = []
        samples = min(100, num_rows // 10)
        
        for i in range(samples):
            key = f"{self.key_prefix}string:{i}"
            start = time.perf_counter()
            await client.get(key)
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "keys_retrieved": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
            "min_time_seconds": round(min(query_times), 4) if query_times else 0,
            "max_time_seconds": round(max(query_times), 4) if query_times else 0
        }
    
    async def _run_pipeline_benchmark(self, client, num_rows: int) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows)
        
        start = time.perf_counter()
        
        pipe = client.pipeline()
        for row in data:
            key = f"{self.key_prefix}pipeline:{row['id']}"
            value = json.dumps(row)
            pipe.set(key, value)
        results = await pipe.execute()
        
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "keys_set": num_rows,
            "time_seconds": round(elapsed, 3),
            "ops_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
        }
    
    async def _run_hash_benchmark(self, client, num_rows: int) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows)
        
        start = time.perf_counter()
        
        for row in data:
            key = f"{self.key_prefix}hash:{row['id']}"
            await client.hset(key, mapping={
                "name": row["name"],
                "email": row["email"],
                "age": str(row["age"]),
                "score": str(row["score"])
            })
        
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "hashes_set": num_rows,
            "time_seconds": round(elapsed, 3),
            "ops_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
        }
    
    async def _run_sorted_set_benchmark(self, client, num_rows: int) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows)
        
        start = time.perf_counter()
        
        key = f"{self.key_prefix}sortedset:leaderboard"
        for row in data:
            await client.zadd(key, {str(row["id"]): row["score"]})
        
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        query_times = []
        
        start = time.perf_counter()
        top_scores = await client.zrevrange(key, 0, 9, withscores=True)
        elapsed = time.perf_counter() - start
        query_times.append(elapsed)
        self._record_query_time(elapsed)
        
        start = time.perf_counter()
        range_scores = await client.zrangebyscore(key, 50, 100, withscores=True)
        elapsed = time.perf_counter() - start
        query_times.append(elapsed)
        self._record_query_time(elapsed)
        
        return {
            "members_added": num_rows,
            "insert_time_seconds": round(elapsed, 3),
            "query_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
        }
    
    async def teardown(self) -> None:
        async with get_redis_connection() as client:
            keys = await client.keys(f"{self.key_prefix}*")
            if keys:
                await client.delete(*keys)
