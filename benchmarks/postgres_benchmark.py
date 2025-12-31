from benchmarks.base import BaseBenchmark
from app.db.postgres import get_postgres_connection
from sqlalchemy import text
from typing import Dict, Any
import time
import io
import csv
import asyncio

class PostgresBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__()
        self.table_name = "benchmark_test"
        
    async def setup(self, config: Dict[str, Any]) -> None:
        async with get_postgres_connection() as session:
            await session.execute(text(f"""
                DROP TABLE IF EXISTS {self.table_name}
            """))
            await session.execute(text(f"""
                CREATE TABLE {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    age INTEGER,
                    score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            await session.execute(text(f"""
                CREATE INDEX idx_name ON {self.table_name}(name)
            """))
            await session.execute(text(f"""
                CREATE INDEX idx_score ON {self.table_name}(score)
            """))
            await session.commit()
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        num_rows = self._get_config_value(config, "rows", 1000)
        operations = self._get_config_value(config, "operations", ["insert", "select"])
        concurrent_users = self._get_config_value(config, "concurrent_users", 1)
        warmup_rows = self._get_config_value(config, "warmup_rows", 0)
        warmup_operations = self._get_config_value(config, "warmup_operations", [])
        steady_state_duration = self._get_config_value(config, "steady_state_duration", 0)
        data_size = self._get_config_value(config, "data_size", "small")
        
        results = {}
        
        # Warm-up phase
        if warmup_rows > 0 and warmup_operations:
            async with get_postgres_connection() as session:
                if "insert" in warmup_operations:
                    await self._run_insert_benchmark(session, warmup_rows, data_size=data_size, warmup=True)
        
        # Main benchmark phase
        async with get_postgres_connection() as session:
            if "insert" in operations:
                insert_result = await self._run_insert_benchmark(
                    session, num_rows, 
                    concurrent_users=concurrent_users,
                    data_size=data_size
                )
                results["insert"] = insert_result
                
            if "select" in operations:
                select_result = await self._run_select_benchmark(
                    session, num_rows,
                    concurrent_users=concurrent_users
                )
                results["select"] = select_result
                
            if "update" in operations:
                update_result = await self._run_update_benchmark(
                    session, num_rows,
                    concurrent_users=concurrent_users
                )
                results["update"] = update_result
                
            if "join" in operations:
                join_result = await self._run_join_benchmark(session)
                results["join"] = join_result
                
            if "window" in operations:
                window_result = await self._run_window_function_benchmark(session)
                results["window"] = window_result
                
            if "json" in operations:
                json_result = await self._run_json_benchmark(session, num_rows)
                results["json"] = json_result
                
            if "fulltext" in operations:
                fulltext_result = await self._run_fulltext_search_benchmark(session, num_rows)
                results["fulltext"] = fulltext_result
        
        # Steady state testing (sustained load)
        if steady_state_duration > 0 and "select" in operations:
            steady_state_result = await self._run_steady_state_benchmark(
                steady_state_duration, concurrent_users
            )
            results["steady_state"] = steady_state_result
        
        return results
    
    async def _run_insert_benchmark(
        self, 
        session, 
        num_rows: int, 
        concurrent_users: int = 1,
        data_size: str = "small",
        warmup: bool = False
    ) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows, data_size=data_size)
        
        async def insert_batch(batch_data):
            values_str = ", ".join([
                f"({row['id']}, '{row['name']}', '{row['email']}', {row['age']}, {row['score']})"
                for row in batch_data
            ])
            await session.execute(text(f"""
                INSERT INTO {self.table_name} (id, name, email, age, score)
                VALUES {values_str}
            """))
        
        start = time.perf_counter()
        
        if concurrent_users > 1:
            # Concurrent batch inserts
            batch_size = max(100, num_rows // (concurrent_users * 10))
            batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]
            
            async def insert_worker(batch):
                await insert_batch(batch)
            
            await asyncio.gather(*[insert_worker(batch) for batch in batches])
        else:
            # Sequential batch inserts
            batch_size = 1000
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                await insert_batch(batch)
        
        await session.commit()
        
        elapsed = time.perf_counter() - start
        if not warmup:
            self._record_query_time(elapsed)
        
        return {
            "rows_inserted": num_rows,
            "time_seconds": round(elapsed, 3),
            "rows_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0,
            "concurrent_users": concurrent_users if not warmup else 0
        }
    
    async def _run_select_benchmark(
        self, 
        session, 
        num_rows: int,
        concurrent_users: int = 1
    ) -> Dict[str, Any]:
        queries = [
            f"SELECT * FROM {self.table_name} WHERE id = :id",
            f"SELECT * FROM {self.table_name} WHERE name = :name",
            f"SELECT * FROM {self.table_name} WHERE score > :score",
            f"SELECT COUNT(*) FROM {self.table_name}",
            f"SELECT AVG(score) FROM {self.table_name}"
        ]
        
        num_queries = min(100, num_rows // 10)
        
        async def execute_query(query_template, query_id):
            if "id = :id" in query_template:
                params = {"id": query_id % num_rows}
            elif "name = :name" in query_template:
                params = {"name": f"user{query_id % num_rows}@example.com"}
            elif "score > :score" in query_template:
                params = {"score": 50}
            else:
                params = {}
            
            start = time.perf_counter()
            await session.execute(text(query_template), params)
            elapsed = time.perf_counter() - start
            self._record_query_time(elapsed)
            return elapsed
        
        if concurrent_users > 1:
            # Concurrent execution
            all_queries = []
            for query_template in queries:
                for i in range(num_queries):
                    all_queries.append((query_template, i))
            
            # Distribute queries across concurrent users
            queries_per_user = len(all_queries) // concurrent_users
            tasks = []
            
            async def query_worker(worker_id):
                worker_times = []
                start_idx = worker_id * queries_per_user
                end_idx = start_idx + queries_per_user if worker_id < concurrent_users - 1 else len(all_queries)
                
                for idx in range(start_idx, end_idx):
                    query_template, query_id = all_queries[idx]
                    elapsed = await execute_query(query_template, query_id)
                    worker_times.append(elapsed)
                return worker_times
            
            for user_id in range(concurrent_users):
                tasks.append(query_worker(user_id))
            
            results = await asyncio.gather(*tasks)
            query_times = [t for worker_times in results for t in worker_times]
        else:
            # Sequential execution
            query_times = []
            for query_template in queries:
                for i in range(num_queries):
                    elapsed = await execute_query(query_template, i)
                    query_times.append(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
            "min_time_seconds": round(min(query_times), 4) if query_times else 0,
            "max_time_seconds": round(max(query_times), 4) if query_times else 0,
            "concurrent_users": concurrent_users
        }
    
    async def _run_update_benchmark(
        self, 
        session, 
        num_rows: int,
        concurrent_users: int = 1
    ) -> Dict[str, Any]:
        updates = min(100, num_rows // 10)
        
        async def execute_update(update_id):
            start = time.perf_counter()
            await session.execute(text(f"""
                UPDATE {self.table_name}
                SET score = score + 1
                WHERE id = :id
            """), {"id": update_id % num_rows})
            await session.commit()
            elapsed = time.perf_counter() - start
            self._record_query_time(elapsed)
            return elapsed
        
        if concurrent_users > 1:
            # Concurrent execution
            updates_per_user = updates // concurrent_users
            tasks = []
            
            async def update_worker(worker_id):
                worker_times = []
                start_idx = worker_id * updates_per_user
                end_idx = start_idx + updates_per_user if worker_id < concurrent_users - 1 else updates
                
                for i in range(start_idx, end_idx):
                    elapsed = await execute_update(i)
                    worker_times.append(elapsed)
                return worker_times
            
            for user_id in range(concurrent_users):
                tasks.append(update_worker(user_id))
            
            results = await asyncio.gather(*tasks)
            query_times = [t for worker_times in results for t in worker_times]
        else:
            # Sequential execution
            query_times = []
            for i in range(updates):
                elapsed = await execute_update(i)
                query_times.append(elapsed)
        
        return {
            "rows_updated": updates,
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
            "concurrent_users": concurrent_users
        }
    
    async def _run_join_benchmark(self, session) -> Dict[str, Any]:
        await session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}_join (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        for i in range(100):
            await session.execute(text(f"""
                INSERT INTO {self.table_name}_join (id, user_id, action)
                VALUES (:id, :user_id, :action)
            """), {"id": i, "user_id": i % 50, "action": "test"})
        await session.commit()
        
        start = time.perf_counter()
        result = await session.execute(text(f"""
            SELECT t.id, t.name, t.score, j.action, j.timestamp
            FROM {self.table_name} t
            JOIN {self.table_name}_join j ON t.id = j.user_id
            WHERE t.score > 50
            LIMIT 100
        """))
        rows = result.fetchall()
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "rows_returned": len(rows),
            "time_seconds": round(elapsed, 3)
        }
    
    async def _run_steady_state_benchmark(
        self,
        duration_seconds: int,
        concurrent_users: int = 1
    ) -> Dict[str, Any]:
        """
        Run sustained load test for specified duration
        """
        end_time = time.perf_counter() + duration_seconds
        query_count = 0
        
        async def steady_state_query():
            nonlocal query_count
            async with get_postgres_connection() as session:
                while time.perf_counter() < end_time:
                    start = time.perf_counter()
                    await session.execute(text(f"""
                        SELECT * FROM {self.table_name} 
                        WHERE id = :id
                    """), {"id": query_count % 1000})
                    elapsed = time.perf_counter() - start
                    self._record_query_time(elapsed)
                    query_count += 1
                    await asyncio.sleep(0.001)  # Small delay to prevent overwhelming
        
        if concurrent_users > 1:
            tasks = [steady_state_query() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
        else:
            await steady_state_query()
        
        return {
            "duration_seconds": duration_seconds,
            "queries_executed": query_count,
            "queries_per_second": round(query_count / duration_seconds, 2) if duration_seconds > 0 else 0,
            "concurrent_users": concurrent_users
        }
    
    async def _run_window_function_benchmark(self, session) -> Dict[str, Any]:
        query_times = []
        
        queries = [
            f"""
            SELECT id, name, score,
                   ROW_NUMBER() OVER (ORDER BY score DESC) as rank,
                   AVG(score) OVER (PARTITION BY age) as avg_by_age
            FROM {self.table_name}
            LIMIT 100
            """,
            f"""
            SELECT id, name, score,
                   LAG(score) OVER (ORDER BY id) as prev_score,
                   LEAD(score) OVER (ORDER BY id) as next_score
            FROM {self.table_name}
            LIMIT 100
            """,
            f"""
            SELECT id, name, score,
                   SUM(score) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as running_sum
            FROM {self.table_name}
            LIMIT 100
            """
        ]
        
        for query in queries:
            start = time.perf_counter()
            await session.execute(text(query))
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
        }
    
    async def _run_json_benchmark(self, session, num_rows: int) -> Dict[str, Any]:
        await session.execute(text(f"""
            ALTER TABLE {self.table_name} 
            ADD COLUMN IF NOT EXISTS metadata JSONB
        """))
        
        for i in range(min(100, num_rows // 10)):
            await session.execute(text(f"""
                UPDATE {self.table_name}
                SET metadata = '{{"tags": ["tag1", "tag2"], "settings": {{"enabled": true}}}}'::jsonb
                WHERE id = :id
            """), {"id": i})
        await session.commit()
        
        query_times = []
        
        queries = [
            f"SELECT * FROM {self.table_name} WHERE metadata->>'tags' LIKE '%tag1%'",
            f"SELECT * FROM {self.table_name} WHERE metadata @> '{{\"settings\": {{\"enabled\": true}}}}'::jsonb",
            f"SELECT id, metadata->'settings'->>'enabled' as enabled FROM {self.table_name} LIMIT 50"
        ]
        
        for query in queries:
            start = time.perf_counter()
            await session.execute(text(query))
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
        }
    
    async def _run_fulltext_search_benchmark(self, session, num_rows: int) -> Dict[str, Any]:
        await session.execute(text(f"""
            ALTER TABLE {self.table_name}
            ADD COLUMN IF NOT EXISTS description TEXT
        """))
        
        await session.execute(text(f"""
            UPDATE {self.table_name}
            SET description = 'This is a test description with various keywords for full text search testing'
            WHERE id < 100
        """))
        await session.commit()
        
        await session.execute(text(f"""
            CREATE INDEX IF NOT EXISTS idx_description_fts 
            ON {self.table_name} USING gin(to_tsvector('english', description))
        """))
        
        query_times = []
        
        queries = [
            f"""
            SELECT id, name, description
            FROM {self.table_name}
            WHERE to_tsvector('english', description) @@ to_tsquery('english', 'test & keywords')
            LIMIT 50
            """,
            f"""
            SELECT id, name, ts_rank(to_tsvector('english', description), 
                   to_tsquery('english', 'search')) as rank
            FROM {self.table_name}
            WHERE to_tsvector('english', description) @@ to_tsquery('english', 'search')
            ORDER BY rank DESC
            LIMIT 50
            """
        ]
        
        for query in queries:
            start = time.perf_counter()
            await session.execute(text(query))
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
        }
    
    async def teardown(self) -> None:
        async with get_postgres_connection() as session:
            await session.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
            await session.execute(text(f"DROP TABLE IF EXISTS {self.table_name}_join"))
            await session.commit()
