from typing import Dict, TYPE_CHECKING, Union, Optional
from dataclasses import asdict
from .context import Context
from .node import PermissionNode, GroupNode

if TYPE_CHECKING:
    from .holder import Holder
    from .group import Group


class PermissionMonitor:
    holders: Dict[str, "Holder"]
    groups: Dict[str, "Group"]

    def __init__(self):
        self.holders = {}
        self.groups = {}

    def add_holder(self, holder: "Holder"):
        self.holders[holder.uid] = holder

    def add_group(self, group: "Group"):
        self.groups[group.name] = group

    def get_holder_groups(self, holder: "Holder", context: Optional[Context] = None):
        ctx = context or Context()
        return [self.groups[i.name.split(":")[-1]] for i in holder.groups[ctx]]

    def check_permission(
            self, holder: "Holder",
            target: Union[str, PermissionNode, GroupNode],
            context: Optional[Context] = None,
    ):
        groups = self.get_holder_groups(holder, context)
        groups.sort(key=lambda x: x.weight, reverse=True)

        if isinstance(target, GroupNode) or (isinstance(target, str) and target.startswith("group:")):
            target = target.name if isinstance(target, GroupNode) else target
            return any(target == g.to_node().name for g in groups)
        if isinstance(target, PermissionNode):
            return next((True for g in groups if target in g.permissions), target in holder.data[context or Context()])
        return next((True for g in groups if g.get_value(target)), holder.get_value(target, context))

    def to_dict(self):
        holders = [asdict(h) for h in self.holders.values()]
        for h in holders:
            h['data'] = {str(k): v for k, v in h['data'].items()}
            h['groups'] = {str(k): v for k, v in h['groups'].items()}
        groups = [asdict(g) for g in self.groups.values()]
        return {"holders": {h["uid"]: h for h in holders}, "groups": {g["name"]: g for g in groups}}


monitor = PermissionMonitor()
