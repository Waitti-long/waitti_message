class User:
    def __init__(self, user_id, username, auth, current_room_name):
        self._user_id = user_id
        self._username = username
        self._auth = auth
        self._current_room_name = current_room_name

    def get_user_id(self):
        return self._user_id

    def get_username(self):
        return self._username

    def get_auth(self):
        return self._auth

    def get_room(self):
        return self._current_room_name

    def set_room(self, dist_room_name):
        self._current_room_name = dist_room_name
