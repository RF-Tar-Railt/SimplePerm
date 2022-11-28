from typing import Dict, Optional
from .base import BasePermissionProcessor


class WildcardProcessor(BasePermissionProcessor):
    RESULT: Optional[bool]
    WILDCARD_SUFFIX = ".*"
    ROOT_WILDCARD = "*"
    ROOT_WILDCARD_WITH_QUOTES = "'*'"

    def __init__(self):
        super().__init__()
        self.wild_perm = {}
        self.root_wildcard_state = None

    @staticmethod
    def is_root_wild(permission: str) -> bool:
        return permission in [WildcardProcessor.ROOT_WILDCARD, WildcardProcessor.ROOT_WILDCARD_WITH_QUOTES]

    @staticmethod
    def is_wild(permission: str) -> bool:
        return WildcardProcessor.is_root_wild(permission) or \
               (permission.endswith(WildcardProcessor.WILDCARD_SUFFIX) and len(permission) > 2)

    wild_perm: Dict[str, Optional[bool]]

    def has_permission(self, permission: str) -> Optional[bool]:
        node = permission
        while 1:
            end_index = node.rfind('.')  # BaseNode.NODE_SEPARATOR
            if end_index == -1:
                break
            node = node[:end_index]
            if node:
                match = self.wild_perm.get(node, -1)
                if match != -1 and match is not None:
                    return match
        return self.root_wildcard_state

    def refresh(self):
        builder = {}
        for k, v in self.source.items():
            if (not k.endswith(self.WILDCARD_SUFFIX)) or len(k) <= 2:
                continue
            k = k[:len(k) - 2]
            value = v.value
            builder[k] = value
        self.wild_perm = builder.copy()
        root_wild = self.source.get(self.ROOT_WILDCARD)
        if not root_wild:
            root_wild = self.source.get(self.ROOT_WILDCARD_WITH_QUOTES)
        self.root_wildcard_state = root_wild.value if root_wild else None
