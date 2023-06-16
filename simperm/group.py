from typing import List, Union, Dict
from dataclasses import dataclass, field
from .node import PermissionNode, GroupNode
from .monitor import monitor


@dataclass(init=False, unsafe_hash=True, eq=True, order=True)
class Group:
    weight: int = field(hash=True, compare=True)
    name: str = field(hash=True, compare=True)
    data: Dict[str, bool] = field(hash=False, compare=False)
    inherit: List[str] = field(hash=False, compare=False)

    def __init__(
        self,
        name: str,
        weight: int,
        *_init: Union[PermissionNode, GroupNode],
    ):
        self.name = name
        self.weight = weight
        self.data = {p.name: p.value for p in _init if isinstance(p, PermissionNode)}
        self.inherit = [
            i.name
            for i in _init
            if isinstance(i, GroupNode) and monitor.get_group(i.name).weight <= weight
        ]
        monitor.add_group(self)

    def to_node(self) -> GroupNode:
        return GroupNode(f"group:{self.name}")

    def add_permission(self, perm: PermissionNode):
        if perm.name not in self.data:
            self.data[perm.name] = perm.value

    def remove_permission(self, perm: str):
        if perm in self.data:
            self.data.pop(perm)

    def get_value(self, perm: str):
        return next((v for n, v in self.data.items() if n == perm), None)

    def change_value(self, perm: PermissionNode):
        if perm.name in self.data:
            self.data[perm.name] = perm.value

    def add_inherit(self, other: Union[GroupNode, "Group", str]):
        target = (
            other
            if isinstance(other, GroupNode)
            else GroupNode(f"group:{other.split(':')[-1]}")
            if isinstance(other, str)
            else other.to_node()
        )
        if target.name not in self.inherit:
            self.inherit.append(target.name)

    def get_inherits(self):
        for ih in self.inherit:
            gp = monitor.get_group(ih)
            if gp.inherit:
                yield from gp.get_inherits()
            yield gp

    def export_permission(self) -> Dict[str, bool]:
        source = self.data.copy()
        gps = list(set(self.get_inherits()))
        gps.sort(key=lambda x: x.weight, reverse=True)
        for gp in gps:
            for k, v in gp.export_permission().items():
                if k not in source or v:
                    source[k] = v
        return source
