
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    private_key: int = -1
    public_key: int = -1
    counter_part_public_key: int = -1
    shared_key: str = ""