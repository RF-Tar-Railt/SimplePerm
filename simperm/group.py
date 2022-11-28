from typing import List, Union, Dict
from dataclasses import dataclass
from .node import PermissionNode, GroupNode
from .monitor import monitor


@dataclass(init=False)
class Group:
    weight: int
    name: str
    data: List[PermissionNode]
    inherit: List[GroupNode]

    def __init__(
        self,
        name: str,
        weight: int,
        *_init: Union[PermissionNode, GroupNode],
    ):
        self.name = name
        self.weight = weight
        self.data = [i for i in _init if isinstance(i, PermissionNode)]
        self.inherit = [
            i
            for i in _init
            if isinstance(i, GroupNode) and monitor.get_group(i.name).weight <= weight
        ]
        monitor.add_group(self)

    def __hash__(self):
        return hash((self.name, self.weight))

    def to_node(self) -> GroupNode:
        return GroupNode(f"group:{self.name}")

    def add_permission(self, perm: PermissionNode):
        if perm not in self.data:
            self.data.append(perm)

    def remove_permission(self, perm: str):
        for p in self.data:
            if p.name == perm:
                self.data.remove(p)
                return

    def get_value(self, perm: str):
        return next((p.value for p in self.data if p.name == perm), False)

    def change_value(self, perm: PermissionNode):
        for p in self.data:
            if p.name == perm.name:
                p.value = perm.value
                return

    def add_inherit(self, other: Union[GroupNode, "Group", str]):
        target = (
            other
            if isinstance(other, GroupNode)
            else GroupNode(f"group:{other.split(':')[-1]}")
            if isinstance(other, str)
            else other.to_node()
        )
        if target not in self.inherit:
            self.inherit.append(target)

    def get_inherits(self):
        for ih in self.inherit:
            gp = monitor.get_group(ih.name)
            if gp.inherit:
                yield from gp.get_inherits()
            yield gp

    def export_permission(self) -> Dict[str, PermissionNode]:
        source = {n.name: n for n in self.data}
        gps = list(set(self.get_inherits()))
        gps.sort(key=lambda x: x.weight, reverse=True)
        for gp in gps:
            add = gp.export_permission()
            for k, v in add.items():
                if k in source and not v.value:
                    continue
                source[k] = v
        return source
