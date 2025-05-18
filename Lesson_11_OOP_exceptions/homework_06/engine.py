"""
create dataclass `Engine`
"""

from dataclasses import dataclass

@dataclass
class Engine:
    volume: float = 0.0
    pistons: int = 0
