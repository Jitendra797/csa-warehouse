from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def upload_file(self, file_bytes: bytes, file_name: str) -> str:
        pass
