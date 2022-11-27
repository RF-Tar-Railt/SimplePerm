from dataclasses import dataclass, field


@dataclass(unsafe_hash=True, eq=True)
class PermissionNode:
    name: str
    value: bool = field(default=True)


@dataclass(unsafe_hash=True, eq=True)
class GroupNode:
    name: str


Permission = PermissionNode
