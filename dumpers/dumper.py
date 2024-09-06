from abc import ABC, abstractmethod
from typing import Dict


class Dumper(ABC):

    @abstractmethod
    def dump(self, data: Dict):
        pass
