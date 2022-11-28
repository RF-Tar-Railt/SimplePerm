from typing import Optional
from .base import BasePermissionProcessor


class DirectProcessor(BasePermissionProcessor):
    def has_permission(self, permission: str) -> Optional[bool]:
        return self.source.get(permission)
