from typing import List, Optional
from dataclasses import dataclass
from .node import PermissionNode, GroupNode
from .monitor import monitor


@dataclass(init=False)
class Group:
    weight: int
    name: str
    permissions: List[PermissionNode]

    def __init__(self, name: str, weight: int, _init: Optional[List[PermissionNode]] = None):
        self.name = name
        self.weight = weight
        self.permissions = _init[:] or []
        monitor.add_group(self)

    def to_node(self) -> GroupNode:
        return GroupNode(f"group:{self.name}")

    def add_permission(self, perm: PermissionNode):
        if perm not in self.permissions:
            self.permissions.append(perm)

    def remove_permission(self, perm: str):
        for p in self.permissions:
            if p.name == perm:
                self.permissions.remove(p)
                return

    def get_value(self, perm: str):
        return next((p.value for p in self.permissions if p.name == perm), False)

    def change_value(self, perm: PermissionNode):
        for p in self.permissions:
            if p.name == perm.name:
                p.value = perm.value
                return
