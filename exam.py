from simperm.user import User
from simperm.group import Group
from simperm.node import Permission
from simperm.monitor import monitor
import json

default = Group("default", 10, Permission("setting.use"))
admin = Group("admin", 40, Permission("setting.change"))
admin.add_inherit(default)

master = Group("master", 50, Permission("setting.*"))

user1 = User("user1")
user1.join_group(default.to_node())

user2 = User("user2")
user2.join_group(admin.to_node())

user3 = User("user3")
user3.join_group(default.to_node())
user3.add_permission(Permission("setting.change", True))

user4 = User("user4")
user4.join_group(master.to_node())

print("------------- level ---------------")
print("user1:", user1.is_in("admin"))
print("user2:", user2.is_in("admin"))
print("------------- perms ---------------")
print("user1: ", monitor.check_permission(user1, "setting.change"))
print("user2: ", monitor.check_permission(user2, "setting.change"))
print("user3: ", monitor.check_permission(user3, "setting.change"))
print("------------- wild ----------------")
print("user4: ", monitor.check_permission(user4, "setting.change"))
print("user4: ", monitor.check_permission(user4, "setting.use"))
with open("data.json", "w+", encoding="utf-8") as f:
    json.dump(monitor.to_dict(), f, ensure_ascii=False, indent=2)
