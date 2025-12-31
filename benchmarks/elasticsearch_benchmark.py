from benchmarks.base import BaseBenchmark
from app.db.elasticsearch import get_elasticsearch_connection
from typing import Dict, Any
import time
import asyncio

class ElasticsearchBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__()
        self.index_name = "benchmark_test"
        
    async def setup(self, config: Dict[str, Any]) -> None:
        def _setup():
            with get_elasticsearch_connection() as client:
                if client.indices.exists(index=self.index_name):
                    client.indices.delete(index=self.index_name)
                client.indices.create(
                    index=self.index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                                "email": {"type": "keyword"},
                                "age": {"type": "integer"},
                                "score": {"type": "integer"},
                                "description": {"type": "text"}
                            }
                        }
                    }
                )
        await asyncio.to_thread(_setup)
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        num_rows = config.get("rows", 1000)
        operations = config.get("operations", ["index", "search"])
        
        results = {}
        
        if "index" in operations:
            index_result = await self._run_index_benchmark(num_rows)
            results["index"] = index_result
            
        if "search" in operations:
            search_result = await self._run_search_benchmark(num_rows)
            results["search"] = search_result
            
        if "aggregate" in operations:
            aggregate_result = await self._run_aggregate_benchmark()
            results["aggregate"] = aggregate_result
            
        if "fulltext" in operations:
            fulltext_result = await self._run_fulltext_search_benchmark()
            results["fulltext"] = fulltext_result
        
        return results
    
    async def _run_index_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _index():
            data = self.generate_test_data(num_rows)
            with get_elasticsearch_connection() as client:
                start = time.perf_counter()
                actions = []
                for row in data:
                    action = {
                        "_index": self.index_name,
                        "_id": row["id"],
                        "_source": {
                            "id": row["id"],
                            "name": row["name"],
                            "email": row["email"],
                            "age": row["age"],
                            "score": row["score"],
                            "description": f"This is a test description for {row['name']} with various keywords"
                        }
                    }
                    actions.append(action)
                from elasticsearch.helpers import bulk
                bulk(client, actions)
                client.indices.refresh(index=self.index_name)
                elapsed = time.perf_counter() - start
                self._record_query_time(elapsed)
                return {
                    "documents_indexed": num_rows,
                    "time_seconds": round(elapsed, 3),
                    "docs_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
                }
        return await asyncio.to_thread(_index)
    
    async def _run_search_benchmark(self, num_rows: int) -> Dict[str, Any]:
        def _search():
            query_times = []
            queries = [
                {"match": {"id": 1}},
                {"term": {"email": "user1@example.com"}},
                {"range": {"score": {"gt": 50}}},
                {"bool": {
                    "must": [
                        {"range": {"age": {"gte": 25, "lte": 50}}},
                        {"range": {"score": {"gt": 30}}}
                    ]
                }}
            ]
            with get_elasticsearch_connection() as client:
                for query in queries:
                    start = time.perf_counter()
                    result = client.search(index=self.index_name, body={"query": query}, size=50)
                    elapsed = time.perf_counter() - start
                    query_times.append(elapsed)
                    self._record_query_time(elapsed)
            return {
                "queries_executed": len(query_times),
                "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
                "min_time_seconds": round(min(query_times), 4) if query_times else 0,
                "max_time_seconds": round(max(query_times), 4) if query_times else 0
            }
        return await asyncio.to_thread(_search)
    
    async def _run_aggregate_benchmark(self) -> Dict[str, Any]:
        def _aggregate():
            with get_elasticsearch_connection() as client:
                start = time.perf_counter()
                result = client.search(
                    index=self.index_name,
                    body={
                        "size": 0,
                        "aggs": {
                            "avg_score": {"avg": {"field": "score"}},
                            "age_groups": {
                                "terms": {"field": "age"},
                                "aggs": {
                                    "avg_score": {"avg": {"field": "score"}}
                                }
                            }
                        }
                    }
                )
                elapsed = time.perf_counter() - start
                self._record_query_time(elapsed)
                return {
                    "time_seconds": round(elapsed, 3),
                    "aggregations": len(result.get("aggregations", {}))
                }
        return await asyncio.to_thread(_aggregate)
    
    async def _run_fulltext_search_benchmark(self) -> Dict[str, Any]:
        def _fulltext():
            query_times = []
            queries = [
                {"match": {"description": "test keywords"}},
                {"multi_match": {
                    "query": "test description",
                    "fields": ["name", "description"]
                }},
                {"match_phrase": {"description": "test description"}}
            ]
            with get_elasticsearch_connection() as client:
                for query in queries:
                    start = time.perf_counter()
                    result = client.search(
                        index=self.index_name,
                        body={"query": query, "highlight": {"fields": {"description": {}}}},
                        size=20
                    )
                    elapsed = time.perf_counter() - start
                    query_times.append(elapsed)
                    self._record_query_time(elapsed)
            return {
                "queries_executed": len(query_times),
                "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
            }
        return await asyncio.to_thread(_fulltext)
    
    async def teardown(self) -> None:
        def _teardown():
            with get_elasticsearch_connection() as client:
                if client.indices.exists(index=self.index_name):
                    client.indices.delete(index=self.index_name)
        await asyncio.to_thread(_teardown)
