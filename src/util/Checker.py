class Checker(object):
    def __init__(self):
        self.id = 'id'
        self.user_nickname = 'nickname'
        self.member_id = 'member_id'

    def key_exit(self, key, json):
        return True if key in json else False

    def check_id(self, json):
        return self.key_exit(self.id, json=json)

    def check_member_id(self, json):
        return self.key_exit(self.member_id, json=json)
