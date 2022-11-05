from dataclasses import dataclass, field
from typing import List, Tuple
from Person import Person
from SecureCommunication import SecureCommunication

@dataclass
class Node:
    secureCommunication: SecureCommunication
    ipaddress: Tuple[str, int]
    files: List[str] = field(default_factory=list)
    public_files: List[str] = field(default_factory=list)

    def dto(self):
        return {
            "name": self.secureCommunication.user.name,
            "ipaddress": self.ipaddress,
            "files": self.files,
            "public_files": self.public_files,
            "public_key": self.secureCommunication.user.public_key
        }