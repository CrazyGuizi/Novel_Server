from pymongo import MongoClient
import json
import time, datetime
import random
from src.Constant import Constant


class MongoUtil(object):
    def __init__(self):
        self.client = MongoClient()
        self.collection = self.client[Constant.MONGO_DB]
        self.novel = self.client[Constant.MONGO_DB][Constant.MONGO_COLLECTION_NOVEL]
        self.novel_temp = self.client[Constant.MONGO_DB][Constant.MONGO_COLLECTION_NOVEL_TEMP]
        self.user = self.collection[Constant.MONGO_COLLECTION_USER]

    # 插入小说
    def novel_add_one(self, one):
        try:
            self.novel.insert_one(one)
        except Exception as e:
            print('插入数据{}出错'.format(one))

    def novel_add_many(self, many):
        try:
            self.novel.insert_many(many)
        except Exception as e:
            print("小说插入多条数据出错")

    def novel_find_all(self):
        try:
            novels = list(self.novel.find({}, {'_id': 0}))
        except Exception as e:
            print('查询全部小说出错')
        return novels if novels else None

    def novel_find_all_from_temp(self):
        try:
            novels = list(self.novel_temp.find({}, {'_id': 0}))
        except Exception as e:
            print('查询全部暂存小说出错')
        return novels if novels else None

    def novel_find_random(self):
        novel_ids = []
        try:
            novels = list(self.novel.find({}, {'_id': 0, 'id': 1}))
        except Exception as e:
            print('随机查找小说出错')

        for i in range(0, 5):
            novel_id = random.choice(novels)['id']
            novel_ids.append(novel_id)
        return novel_ids

    def novel_insert_my(self, member_id, book_ids):
        if isinstance(book_ids, list):
            self.user.update_one(
                {'id': member_id},
                {
                    '$addToSet': {'books': {'$each': book_ids}}
                }
            )
        else:
            self.user.update_one(
                {'id': member_id},
                {
                    '$addToSet': {'books': book_ids}
                }
            )

    def novel_find_by_ids(self, ids):
        return self.novel.find({'id': {'$in': ids}}, {'_id': 0, 'chapters.content': 0})

    def novel_find_by_user(self, member_id, first):
        # 用户第一次使用
        if first:
            books = self.novel_find_random()
            if not books:
                return []

            self.novel_insert_my(member_id, books)
            self.user.update_one(
                {"id": member_id},
                {'$set': {'first': False}}
            )

            myBooks = list(self.novel_find_by_ids(books))
            return myBooks

        # 查询该用户的书
        try:
            books = self.user.find_one({'id': member_id}, {'_id': 0, 'books': 1})['books']
            if books:
                myBooks = list(self.novel_find_by_ids(books))
        except Exception as e:
            print('查询用户{}的小说出错'.format(member_id))

        return myBooks

    def user_get_last_id(self):
        last_id = self.user.find({}, {'_id': 0, 'id': 1}).sort([('id', -1)]).limit(1)
        return 0 if last_id.count() == 0 else last_id[0]['id']

    def user_register(self, info):
        user_id = self.user_get_last_id() + 1
        info['id'] = user_id
        info['nickname'] = '悦读{}号'.format(user_id)
        info['createTime'] = int(time.time() * 1000)
        try:
            self.user.insert_one(info)
        except Exception as e:
            print('注册失败')
            return None

        return self.user_find_by_id(user_id)

    def user_login(self, tel, psw):
        user = self.user.find_one({'tel': tel, 'password': psw})
        return user

    def user_find_by_id(self, id):
        user = self.user.find_one({'id': id}, {'_id': 0})
        return user

    def user_find_by_tel(self, tel):
        user = self.user.find_one({'tel': tel})
        return user if user else None

    def user_find_by_tel_psw(self, tel, psw):
        user = self.user.find_one({'tel': tel, 'password': psw}, {'_id': 0})
        return user if user else None


if __name__ == '__main__':
    mg = MongoUtil()
    myBooks = mg.novel_find_by_user(1, False)
    print(list(myBooks))
