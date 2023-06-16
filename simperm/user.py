from typing import Dict, Optional, List, Union
from dataclasses import dataclass, field
from .context import Context
from .monitor import monitor
from .node import PermissionNode, GroupNode


@dataclass(init=False, unsafe_hash=True, eq=True)
class User:
    uid: str = field(compare=True, hash=True)
    data: Dict[Context, Dict[str, bool]] = field(compare=False, hash=False)
    groups: Dict[Context, List[str]] = field(compare=False, hash=False)

    def __init__(
        self,
        uid: str,
        _init: Optional[Dict[Context, List[Union[PermissionNode, GroupNode]]]] = None,
    ):
        self.uid = uid
        monitor.add_holder(self)
        self.data = {}
        self.groups = {}
        for ctx, nodes in _init or {}:
            self.data[ctx] = {n.name: n.value for n in nodes if isinstance(n, PermissionNode)}
            self.groups[ctx] = [n.name for n in nodes if isinstance(n, GroupNode)]

    def add_permission(self, perm: PermissionNode, context: Optional[Context] = None):
        if perm.name not in (perms := self.data.setdefault(context or Context(), {})):
            perms[perm.name] = perm.value

    def remove_permission(self, perm: str, context: Optional[Context] = None):
        if perm in (perms := self.data.setdefault(context or Context(), {})):
            perms.pop(perm)

    def join_group(
        self, group: Union[str, GroupNode], context: Optional[Context] = None
    ):
        target = (
            group
            if isinstance(group, GroupNode)
            else GroupNode(f"group:{group.split(':')[-1]}")
        )
        if target.name not in (groups := self.groups.setdefault(context or Context(), [])):
            groups.append(target.name)

    def leave_group(
        self, group: Union[str, GroupNode], context: Optional[Context] = None
    ):
        target = (
            group
            if isinstance(group, GroupNode)
            else GroupNode(f"group:{group.split(':')[-1]}")
        )
        if target.name in (groups := self.groups.get(context or Context(), [])):
            groups.remove(target.name)

    def get_value(self, perm: str, context: Optional[Context] = None):
        perms = self.data.get(context or Context(), {})
        return next((v for n, v in perms.items() if n == perm), None)

    def change_value(self, perm: PermissionNode, context: Optional[Context] = None):
        if perm.name in (perms := self.data.setdefault(context or Context(), {})):
            perms[perm.name] = perm.value

    def is_in(self, group: Union[str, GroupNode], context: Optional[Context] = None):
        target = (
            group
            if isinstance(group, GroupNode)
            else GroupNode(f"group:{group.split(':')[-1]}")
        )
        for gp in self.groups.get(context or Context(), []):
            if target.name == gp:
                return True
            for ih in monitor.get_group(gp).get_inherits():
                if ih.to_node() == target:
                    return True
        return False

    def export_permission(self, context: Optional[Context] = None):
        ctx = context or Context()
        source = self.data.get(ctx, {}).copy()
        gps = [monitor.get_group(gp) for gp in self.groups.get(ctx, [])]
        gps.sort(key=lambda x: x.weight, reverse=True)
        for gp in gps:
            for k, v in gp.export_permission().items():
                if k not in source or v:
                    source[k] = v
        return source
