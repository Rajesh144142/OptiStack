from benchmarks.base import BaseBenchmark
from app.db.mongodb import get_mongodb_connection
from typing import Dict, Any
import time

class MongoDBBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__()
        self.collection_name = "benchmark_test"
        
    async def setup(self, config: Dict[str, Any]) -> None:
        async with get_mongodb_connection() as db:
            collection = db[self.collection_name]
            await collection.drop()
            await collection.create_index("id")
            await collection.create_index("name")
            await collection.create_index("score")
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        num_rows = config.get("rows", 1000)
        operations = config.get("operations", ["insert", "select"])
        
        results = {}
        
        async with get_mongodb_connection() as db:
            collection = db[self.collection_name]
            
            if "insert" in operations:
                insert_result = await self._run_insert_benchmark(collection, num_rows)
                results["insert"] = insert_result
                
            if "select" in operations:
                select_result = await self._run_select_benchmark(collection, num_rows)
                results["select"] = select_result
                
            if "update" in operations:
                update_result = await self._run_update_benchmark(collection, num_rows)
                results["update"] = update_result
                
            if "aggregate" in operations:
                aggregate_result = await self._run_aggregate_benchmark(collection)
                results["aggregate"] = aggregate_result
                
            if "lookup" in operations:
                lookup_result = await self._run_lookup_benchmark(db)
                results["lookup"] = lookup_result
                
            if "textsearch" in operations:
                textsearch_result = await self._run_text_search_benchmark(collection, num_rows)
                results["textsearch"] = textsearch_result
        
        return results
    
    async def _run_insert_benchmark(self, collection, num_rows: int) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows)
        documents = [
            {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "age": row["age"],
                "score": row["score"]
            }
            for row in data
        ]
        
        start = time.perf_counter()
        await collection.insert_many(documents, ordered=False)
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "documents_inserted": num_rows,
            "time_seconds": round(elapsed, 3),
            "docs_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
        }
    
    async def _run_select_benchmark(self, collection, num_rows: int) -> Dict[str, Any]:
        query_times = []
        
        for i in range(min(100, num_rows // 10)):
            start = time.perf_counter()
            await collection.find_one({"id": i})
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        for i in range(min(50, num_rows // 20)):
            start = time.perf_counter()
            await collection.find({"score": {"$gt": 50}}).limit(10).to_list(length=10)
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
            "min_time_seconds": round(min(query_times), 4) if query_times else 0,
            "max_time_seconds": round(max(query_times), 4) if query_times else 0
        }
    
    async def _run_update_benchmark(self, collection, num_rows: int) -> Dict[str, Any]:
        updates = min(100, num_rows // 10)
        query_times = []
        
        for i in range(updates):
            start = time.perf_counter()
            await collection.update_one(
                {"id": i},
                {"$inc": {"score": 1}}
            )
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "documents_updated": updates,
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
        }
    
    async def _run_aggregate_benchmark(self, collection) -> Dict[str, Any]:
        start = time.perf_counter()
        result = await collection.aggregate([
            {"$match": {"score": {"$gt": 50}}},
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$score"},
                "count": {"$sum": 1}
            }}
        ]).to_list(length=100)
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "time_seconds": round(elapsed, 3),
            "results": len(result)
        }
    
    async def _run_lookup_benchmark(self, db) -> Dict[str, Any]:
        orders_collection = db["benchmark_orders"]
        await orders_collection.drop()
        
        for i in range(100):
            await orders_collection.insert_one({
                "order_id": i,
                "user_id": i % 50,
                "amount": i * 10,
                "status": "completed" if i % 2 == 0 else "pending"
            })
        
        users_collection = db[self.collection_name]
        
        start = time.perf_counter()
        result = await users_collection.aggregate([
            {"$match": {"id": {"$lt": 50}}},
            {"$lookup": {
                "from": "benchmark_orders",
                "localField": "id",
                "foreignField": "user_id",
                "as": "orders"
            }},
            {"$unwind": "$orders"},
            {"$group": {
                "_id": "$id",
                "total_orders": {"$sum": 1},
                "total_amount": {"$sum": "$orders.amount"}
            }},
            {"$limit": 50}
        ]).to_list(length=50)
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        await orders_collection.drop()
        
        return {
            "results_returned": len(result),
            "time_seconds": round(elapsed, 3)
        }
    
    async def _run_text_search_benchmark(self, collection, num_rows: int) -> Dict[str, Any]:
        try:
            await collection.create_index([("name", "text"), ("email", "text")])
        except Exception:
            pass
        
        query_times = []
        
        search_terms = ["user", "test", "example"]
        for term in search_terms:
            start = time.perf_counter()
            await collection.find({"$text": {"$search": term}}).limit(20).to_list(length=20)
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
        }
    
    async def teardown(self) -> None:
        async with get_mongodb_connection() as db:
            collection = db[self.collection_name]
            await collection.drop()
            orders_collection = db.get_collection("benchmark_orders")
            if orders_collection:
                await orders_collection.drop()
