from dataclasses import dataclass

from app import constants


@dataclass(frozen=True)
class Url:
    endpoint: str
    version: str = constants.API_VERSION

    def __str__(self) -> str:
        return f'http://{constants.SERVICE_IP_ADDRESS}/{self.version}/{self.endpoint}'
