from dataclasses import dataclass


@dataclass
class ApiEndpoints:
    PING: str = "/ping"
    HEALTH: str = "/health"
    RUN: str = "/run"
    STATUS: str = "/status"
    TRAIN: str = "/train"


endpoints = ApiEndpoints()
