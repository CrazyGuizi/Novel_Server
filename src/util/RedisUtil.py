import redis


class RedisUtil(object):
    def __init__(self):
        self.client = redis.Redis()

    def save_index_url(self, key_name, url_list):
        self.client.rpush(key_name, *url_list)

    def get_index_urls(self, key_name):
        urls = []
        try:
            urls = self.client.lrange(key_name, 0, -1)
        except Exception as e:
            print('读取index_urls出错')
        return urls
