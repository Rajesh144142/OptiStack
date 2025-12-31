from benchmarks.base import BaseBenchmark
from app.db.postgres import get_postgres_connection
from sqlalchemy import text
from typing import Dict, Any
import time
import io
import csv

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
        num_rows = config.get("rows", 1000)
        operations = config.get("operations", ["insert", "select"])
        
        results = {}
        
        async with get_postgres_connection() as session:
            if "insert" in operations:
                insert_result = await self._run_insert_benchmark(session, num_rows)
                results["insert"] = insert_result
                
            if "select" in operations:
                select_result = await self._run_select_benchmark(session, num_rows)
                results["select"] = select_result
                
            if "update" in operations:
                update_result = await self._run_update_benchmark(session, num_rows)
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
        
        return results
    
    async def _run_insert_benchmark(self, session, num_rows: int) -> Dict[str, Any]:
        data = self.generate_test_data(num_rows)
        
        start = time.perf_counter()
        
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            values_str = ", ".join([
                f"({row['id']}, '{row['name']}', '{row['email']}', {row['age']}, {row['score']})"
                for row in batch
            ])
            await session.execute(text(f"""
                INSERT INTO {self.table_name} (id, name, email, age, score)
                VALUES {values_str}
            """))
        
        await session.commit()
        
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        
        return {
            "rows_inserted": num_rows,
            "time_seconds": round(elapsed, 3),
            "rows_per_second": round(num_rows / elapsed, 2) if elapsed > 0 else 0
        }
    
    async def _run_select_benchmark(self, session, num_rows: int) -> Dict[str, Any]:
        queries = [
            f"SELECT * FROM {self.table_name} WHERE id = :id",
            f"SELECT * FROM {self.table_name} WHERE name = :name",
            f"SELECT * FROM {self.table_name} WHERE score > :score",
            f"SELECT COUNT(*) FROM {self.table_name}",
            f"SELECT AVG(score) FROM {self.table_name}"
        ]
        
        query_times = []
        
        for query_template in queries:
            for i in range(min(100, num_rows // 10)):
                if "id = :id" in query_template:
                    params = {"id": i}
                elif "name = :name" in query_template:
                    params = {"name": f"user{i}@example.com"}
                elif "score > :score" in query_template:
                    params = {"score": 50}
                else:
                    params = {}
                
                start = time.perf_counter()
                await session.execute(text(query_template), params)
                elapsed = time.perf_counter() - start
                query_times.append(elapsed)
                self._record_query_time(elapsed)
        
        return {
            "queries_executed": len(query_times),
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0,
            "min_time_seconds": round(min(query_times), 4) if query_times else 0,
            "max_time_seconds": round(max(query_times), 4) if query_times else 0
        }
    
    async def _run_update_benchmark(self, session, num_rows: int) -> Dict[str, Any]:
        updates = min(100, num_rows // 10)
        query_times = []
        
        for i in range(updates):
            start = time.perf_counter()
            await session.execute(text(f"""
                UPDATE {self.table_name}
                SET score = score + 1
                WHERE id = :id
            """), {"id": i})
            await session.commit()
            elapsed = time.perf_counter() - start
            query_times.append(elapsed)
            self._record_query_time(elapsed)
        
        return {
            "rows_updated": updates,
            "avg_time_seconds": round(sum(query_times) / len(query_times), 4) if query_times else 0
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
