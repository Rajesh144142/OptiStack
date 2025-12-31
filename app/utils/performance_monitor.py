import time
import psutil
import threading
from typing import List, Dict, Any, Optional
from collections import deque

class PerformanceMonitor:
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.query_times: List[float] = []
        self.cpu_samples: deque = deque(maxlen=1000)
        self.memory_samples: deque = deque(maxlen=1000)
        self.sampling_active = False
        self.sampling_thread: Optional[threading.Thread] = None
        self.process = psutil.Process()
        
    def start_experiment(self):
        self.start_time = time.perf_counter()
        self.query_times.clear()
        self.cpu_samples.clear()
        self.memory_samples.clear()
        self._start_sampling()
        
    def stop_experiment(self):
        self.end_time = time.perf_counter()
        self._stop_sampling()
        
    def record_query_time(self, query_time: float):
        self.query_times.append(query_time)
        
    def _start_sampling(self):
        self.sampling_active = True
        self.sampling_thread = threading.Thread(target=self._sample_resources, daemon=True)
        self.sampling_thread.start()
        
    def _stop_sampling(self):
        self.sampling_active = False
        if self.sampling_thread:
            self.sampling_thread.join(timeout=1.0)
            
    def _sample_resources(self):
        while self.sampling_active:
            try:
                self.cpu_samples.append(self.process.cpu_percent(interval=0.1))
                self.memory_samples.append(self.process.memory_info().rss / 1024 / 1024)
            except Exception:
                pass
            time.sleep(0.5)
            
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_results(self) -> Dict[str, Any]:
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0.0
        
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
        max_cpu = max(self.cpu_samples) if self.cpu_samples else 0.0
        avg_memory = sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0.0
        max_memory = max(self.memory_samples) if self.memory_samples else 0.0
        
        if self.query_times:
            total_queries = len(self.query_times)
            ops_per_second = total_queries / duration if duration > 0 else 0.0
            avg_latency = sum(self.query_times) / total_queries
            p50_latency = self._calculate_percentile(self.query_times, 50)
            p95_latency = self._calculate_percentile(self.query_times, 95)
            p99_latency = self._calculate_percentile(self.query_times, 99)
        else:
            total_queries = 0
            ops_per_second = 0.0
            avg_latency = 0.0
            p50_latency = 0.0
            p95_latency = 0.0
            p99_latency = 0.0
            
        return {
            "duration_seconds": round(duration, 3),
            "total_queries": total_queries,
            "ops_per_second": round(ops_per_second, 2),
            "latency_ms": {
                "avg": round(avg_latency * 1000, 2),
                "p50": round(p50_latency * 1000, 2),
                "p95": round(p95_latency * 1000, 2),
                "p99": round(p99_latency * 1000, 2)
            },
            "cpu_percent": {
                "avg": round(avg_cpu, 2),
                "max": round(max_cpu, 2)
            },
            "memory_mb": {
                "avg": round(avg_memory, 2),
                "max": round(max_memory, 2)
            }
        }

