from abc import ABCMeta, abstractmethod
from typing import Dict, Optional
from ..node import Permission


class BasePermissionProcessor(metaclass=ABCMeta):

    def __init__(self):
        self.source: Dict[str, Permission] = {}

    def set_source(self, source: Dict[str, Permission]):
        self.source = source

    def entry(self, prev: Optional[bool], permission: str) -> Optional[bool]:
        if prev is not None:
            return self.has_perm_override(prev, permission)
        return self.has_permission(permission)

    @abstractmethod
    def has_permission(self, permission: str) -> Optional[bool]:
        ...

    def has_perm_override(self, prev: Optional[bool], permission: str) -> Optional[bool]:  # noqa
        return prev

    def refresh(self):
        ...
