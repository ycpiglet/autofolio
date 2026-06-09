from dataclasses import dataclass


@dataclass(frozen=True)
class KisEnvironment:
    name: str
    base_url: str
