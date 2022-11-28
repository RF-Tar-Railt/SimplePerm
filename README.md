# simple-permission

A simple impl of permission system, inspired from Luckperm

## example

group:

```python
from simperm import Group, Permission

# group:default have one basic perm setting.check
default = Group("default", 10, Permission("setting.check"))
# group:admin inherit default and have another perm setting.change
admin = Group("admin", 40, default.to_node(), Permission("setting.change"))
# group:owner include admin (and so include default)
owner = Group("owner", 80, admin.to_node(), Permission("setting.add"), Permission("setting.remove"))
# user in group:master can have all access of setting permission
master = Group("master", 100, Permission("setting.*"), Permission("permission.*"))
```

user:
```python
from simperm import User, Permission, Context, monitor

user1 = User("user1")
# user1 can get all permission in group:default
user1.join_group(default.to_node())
user2 = User("user2")
user2.join_group(default.to_node())
user2.add_permission(Permission("setting.add"))
# user2 can only get admin's permissions when context is scope:main
user2.join_group(admin.to_node(), Context(scope="main"))

assert not monitor.check_permission(user1, "setting.change")
assert not monitor.check_permission(user2, "setting.change", context=Context(scope="sub"))
```