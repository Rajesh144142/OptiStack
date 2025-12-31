from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import random
import string

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
    
    def generate_test_data(self, num_rows: int, num_fields: int = 5) -> List[Dict[str, Any]]:
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
                row[f"field_{j}"] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            data.append(row)
        return data

