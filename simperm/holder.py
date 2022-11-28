from typing import Dict, Optional, List, Union
from dataclasses import dataclass
from .context import Context
from .monitor import monitor
from .node import PermissionNode, GroupNode


@dataclass(init=False)
class User:
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

    def __hash__(self):
        return hash(self.uid)

    def add_permission(self, perm: PermissionNode, context: Optional[Context] = None):
        if perm not in (perms := self.data.setdefault(context or Context(), [])):
            perms.append(perm)

    def remove_permission(self, perm: str, context: Optional[Context] = None):
        perms = self.data.get(context or Context(), [])
        for p in perms:
            if p.name == perm:
                perms.remove(p)
                return

    def join_group(self, group: Union[str, GroupNode], context: Optional[Context] = None):
        target = group if isinstance(group, GroupNode) else GroupNode(f"group:{group.split(':')[-1]}")
        if target not in (groups := self.groups.setdefault(context or Context(), [])):
            groups.append(target)

    def leave_group(self, group: Union[str, GroupNode], context: Optional[Context] = None):
        target = group if isinstance(group, GroupNode) else GroupNode(f"group:{group.split(':')[-1]}")
        if target in (groups := self.groups.get(context or Context(), [])):
            groups.remove(target)

    def get_value(self, perm: str, context: Optional[Context] = None):
        perms = self.data.get(context or Context(), [])
        return next((p.value for p in perms if p.name == perm), False)

    def change_value(self, perm: PermissionNode, context: Optional[Context] = None):
        perms = self.data.get(context or Context(), [])
        for p in perms:
            if p.name == perm.name:
                p.value = perm.value
                return

    def is_in(self, group: Union[str, GroupNode], context: Optional[Context] = None):
        group = group if isinstance(group, GroupNode) else GroupNode(f"group:{group.split(':')[-1]}")
        gps = self.groups.get(context or Context(), [])
        for gp in gps:
            if group == gp:
                return True
            for ih in monitor.get_group(gp.name).get_inherits():
                if ih.to_node() == group:
                    return True
        return False

    def export_permission(self, context: Optional[Context] = None):
        ctx = context or Context()
        source = {n.name: n for n in self.data.get(ctx, [])}
        gps = [monitor.get_group(gp.name) for gp in self.groups.get(ctx, [])]
        gps.sort(key=lambda x: x.weight, reverse=True)
        for gp in gps:
            add = gp.export_permission()
            for k, v in add.items():
                if k in source and not v.value:
                    continue
                source[k] = v
        return source
