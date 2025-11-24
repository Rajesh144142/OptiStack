from benchmarks.base import BaseBenchmark
from typing import Dict, Any

class CockroachDBBenchmark(BaseBenchmark):
    async def setup(self, config: Dict[str, Any]) -> None:
        pass
    
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    async def teardown(self) -> None:
        pass

