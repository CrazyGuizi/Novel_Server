import json


class NetUtil(object):
    def __init__(self):
        pass

    def success(self, code=0, message='成功', data=None):
        return self.__build(code, message, data)

    def fail(self, code=-1, message='失败', data=None):
        return self.__build(code, message, data)

    def __build(self, code, message, data):
        return json.dumps({
            'code': code,
            'message': message,
            'data': data
        }, ensure_ascii=False)
