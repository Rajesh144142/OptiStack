from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseBenchmark(ABC):
    @abstractmethod
    async def setup(self, config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def teardown(self) -> None:
        pass

