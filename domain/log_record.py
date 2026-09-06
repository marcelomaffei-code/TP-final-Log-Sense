from abc import ABC,abstractmethod
class LogRecord(ABC):
    def __init__(self,timestamp,origin): self._timestamp=timestamp; self._origin=origin
    @property
    def timestamp(self): return self._timestamp
    @property
    def origin(self): return self._origin
    @abstractmethod
    def calculate_level(self): ...
