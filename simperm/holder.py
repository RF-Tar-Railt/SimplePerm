from typing import Dict, Optional, List, Union
from dataclasses import dataclass
from .context import Context
from .monitor import monitor
from .node import PermissionNode, GroupNode


@dataclass(init=False)
class Holder:
    uid: str
    data: Dict[Context, List[PermissionNode]]
    groups: Dict[Context, List[GroupNode]]

    def __init__(
        self,
        uid: str,
        _init: Optional[Dict[Context, List[Union[PermissionNode, GroupNode]]]] = None
    ):
        self.uid = uid
        monitor.add_holder(self)
        self.data = {}
        self.groups = {}
        for ctx, nodes in (_init or {}):
            self.data[ctx] = [n for n in nodes if isinstance(n, PermissionNode)]
            self.groups[ctx] = [n for n in nodes if isinstance(n, GroupNode)]

    def add_permission(self, perm: PermissionNode, context: Optional[Context] = None):
        if perm not in (perms := self.data.setdefault(context or Context(), [])):
            perms.append(perm)

    def remove_permission(self, perm: str, context: Optional[Context] = None):
        perms = self.data.setdefault(context or Context(), [])
        for p in perms:
            if p.name == perm:
                perms.remove(p)
                return

    def join_group(self, group: GroupNode, context: Optional[Context] = None):
        if group not in (groups := self.groups.setdefault(context or Context(), [])):
            groups.append(group)

    def leave_group(self, group: Union[str, GroupNode], context: Optional[Context] = None):
        group = group if isinstance(group, GroupNode) else GroupNode(f"group:{group}")
        groups = self.groups.setdefault(context or Context(), [])
        for g in groups:
            if g.name == group:
                groups.remove(g)
                return

    def get_value(self, perm: str, context: Optional[Context] = None):
        perms = self.data.setdefault(context or Context(), [])
        return next((p.value for p in perms if p.name == perm), False)

    def change_value(self, perm: PermissionNode, context: Optional[Context] = None):
        perms = self.data.setdefault(context or Context(), [])
        for p in perms:
            if p.name == perm.name:
                p.value = perm.value
                return

    def is_in(self, group: Union[str, GroupNode], context: Optional[Context] = None):
        group = group if isinstance(group, GroupNode) else GroupNode(f"group:{group}")
        return group in self.groups.setdefault(context or Context(), [])
