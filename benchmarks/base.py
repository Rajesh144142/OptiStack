from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import time
import random
import string
import asyncio
from concurrent.futures import ThreadPoolExecutor
import math

class BaseBenchmark(ABC):
    def __init__(self):
        self.monitor = None
        
    def set_monitor(self, monitor):
        self.monitor = monitor
    
    @abstractmethod
    async def setup(self, config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def teardown(self) -> None:
        pass
    
    def _record_query_time(self, query_time: float):
        if self.monitor:
            self.monitor.record_query_time(query_time)
    
    def _time_operation(self, func, *args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        self._record_query_time(elapsed)
        return result, elapsed
    
    def generate_test_data(self, num_rows: int, num_fields: int = 5, data_size: str = "small") -> List[Dict[str, Any]]:
        """
        Generate test data with configurable complexity
        
        Args:
            num_rows: Number of rows to generate
            num_fields: Number of fields per row
            data_size: "small", "medium", or "large" - affects field sizes
        """
        field_size_map = {
            "small": 10,
            "medium": 50,
            "large": 200
        }
        field_size = field_size_map.get(data_size, 10)
        
        data = []
        for i in range(num_rows):
            row = {
                "id": i,
                "name": ''.join(random.choices(string.ascii_letters, k=20)),
                "email": f"user{i}@example.com",
                "age": random.randint(18, 80),
                "score": random.randint(0, 100)
            }
            for j in range(num_fields - 5):
                row[f"field_{j}"] = ''.join(random.choices(string.ascii_letters + string.digits, k=field_size))
            data.append(row)
        return data
    
    async def _run_concurrent_operations(
        self,
        operation_func: Callable,
        num_operations: int,
        concurrent_users: int = 1,
        **kwargs
    ) -> List[float]:
        """
        Run operations concurrently with specified number of users
        
        Args:
            operation_func: Async function to execute
            num_operations: Total number of operations to perform
            concurrent_users: Number of concurrent users/threads
            **kwargs: Additional arguments to pass to operation_func
            
        Returns:
            List of operation durations
        """
        if concurrent_users <= 1:
            # Sequential execution
            durations = []
            for _ in range(num_operations):
                start = time.perf_counter()
                await operation_func(**kwargs)
                elapsed = time.perf_counter() - start
                durations.append(elapsed)
                self._record_query_time(elapsed)
            return durations
        
        # Concurrent execution
        operations_per_user = math.ceil(num_operations / concurrent_users)
        tasks = []
        
        async def worker(worker_id: int):
            worker_durations = []
            start_idx = worker_id * operations_per_user
            end_idx = min(start_idx + operations_per_user, num_operations)
            
            for i in range(start_idx, end_idx):
                start = time.perf_counter()
                await operation_func(**kwargs)
                elapsed = time.perf_counter() - start
                worker_durations.append(elapsed)
                self._record_query_time(elapsed)
            return worker_durations
        
        # Create tasks for all workers
        for user_id in range(concurrent_users):
            tasks.append(worker(user_id))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_durations = []
        for worker_durations in results:
            all_durations.extend(worker_durations)
        
        return all_durations[:num_operations]  # Ensure we don't exceed requested operations
    
    def _get_config_value(self, config: Dict[str, Any], key: str, default: Any) -> Any:
        """Helper to safely get config values with defaults"""
        return config.get(key, default)

