from simperm.holder import Holder
from simperm.group import Group
from simperm.node import Permission
from simperm.monitor import monitor
import json

default = Group("default", 10, [Permission("setting.use")])
admin = Group("admin", 40, default.permissions)
admin.add_permission(Permission("setting.change"))

user1 = Holder("user1")
user1.join_group(default.to_node())
user2 = Holder("user2")
user2.join_group(default.to_node())
user2.join_group(admin.to_node())
user3 = Holder("user3")
user3.join_group(default.to_node())
user3.add_permission(Permission("setting.change"))

print("------------- level ---------------")
print("user1:", monitor.check_permission(user1, "group:admin"))
print("user2:", monitor.check_permission(user2, "group:admin"))
print("------------- perms ---------------")
print("user1: ", monitor.check_permission(user1, "setting.change"))
print("user2: ", monitor.check_permission(user2, "setting.change"))
print("user3: ", monitor.check_permission(user3, "setting.change"))

# with open("data.json", "w+", encoding="utf-8") as f:
#     json.dump(monitor.to_dict(), f, ensure_ascii=False, indent=2)
