class Room:
    """用以保存房间内的用户数据以及当前状态"""

    def __init__(self, room_name):
        self._name = room_name
        self._users = []

    def add_user(self, user):
        self._users.append(user)

    def remove_user(self, user):
        self._users.remove(user)

    def list_users(self):
        return self._users

    def has_user(self, username):
        for user in self._users:
            if user.get_username() == username:
                return True
        return False
