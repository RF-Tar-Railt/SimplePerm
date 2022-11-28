from typing import Dict, TYPE_CHECKING, Union, Optional
from dataclasses import asdict
from .context import Context
from .calculator import PermissionCalculator
from .processor import WildcardProcessor, DirectProcessor
from .node import PermissionNode

if TYPE_CHECKING:
    from .holder import User
    from .group import Group


class PermissionMonitor:
    holders: Dict[str, "User"]
    groups: Dict[str, "Group"]
    calculator: PermissionCalculator

    def __init__(self):
        self.holders = {}
        self.groups = {}
        self.calculator = PermissionCalculator([DirectProcessor(), WildcardProcessor()])

    def add_holder(self, holder: "User"):
        self.holders[holder.uid] = holder

    def add_group(self, group: "Group"):
        self.groups[group.name] = group

    def get_group(self, name: str):
        return self.groups[name.split(":")[-1]]

    def to_dict(self):
        holders = [asdict(h) for h in self.holders.values()]
        for h in holders:
            h['data'] = {str(k): v for k, v in h['data'].items()}
            h['groups'] = {str(k): v for k, v in h['groups'].items()}
        groups = [asdict(g) for g in self.groups.values()]
        return {"holders": {h["uid"]: h for h in holders}, "groups": {g["name"]: g for g in groups}}

    def check_permission(
            self,
            holder: "User",
            target: Union[str, PermissionNode],
            context: Optional[Context] = None,
            calculator: Optional[PermissionCalculator] = None
    ):
        cal = calculator or self.calculator
        if not target:
            raise ValueError
        source = holder.export_permission(context)
        cal.set_root_permission(source)
        if isinstance(target, str):
            if target.startswith("group:"):
                return holder.is_in(target)
            return cal.check_permission(target)
        return target.value == cal.check_permission(target.name)


monitor = PermissionMonitor()
