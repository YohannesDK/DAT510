
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Person:
    name: str
    private_key: int = -1
    public_key: int = -1
    peers_public_keys: Dict[str, int] = field(default_factory=dict)
    peers_shared_keys: Dict[str, bytes] = field(default_factory=dict)