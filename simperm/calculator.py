from typing import List, Dict, Optional
from .node import Permission
from .processor import BasePermissionProcessor


class PermissionCalculator:
    processors: List[BasePermissionProcessor]

    def __init__(
        self,
        processors: List[BasePermissionProcessor]
    ):
        self.processors = processors

    def check_permission(self, permission: str) -> Optional[bool]:
        permission = permission.lower()
        result = None
        for processor in self.processors:
            result = processor.entry(result, permission)
        return result

    def set_root_permission(self, source: Dict[str, Permission]):
        for processor in self.processors:
            processor.set_source(source)
            processor.refresh()
