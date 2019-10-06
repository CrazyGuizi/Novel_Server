from flask import Flask, request
from src.util import Checker
from src.util import NetUtil
from src.util import MongoUtil

app = Flask(__name__)
app.debug = True
checker = Checker.Checker()
mgUtil = MongoUtil.MongoUtil()
netUtil = NetUtil.NetUtil()


@app.route('/test/', methods=['POST'])
def test():
    json = request.json
    return netUtil.success(message='成功', data=json)


@app.route('/novel/addMy', methods=['POST'])
def novel_add_my():
    json = request.json
    novel = mgUtil.novel_insert_my(json['member_id'], json['book_id'])
    if novel:
        return netUtil.success(message='添加成功', data=novel)
    else:
        return netUtil.fail(message='添加失败')


@app.route('/novel/my', methods=['POST'])
def get_my_books():
    json = request.json
    if checker.check_member_id(json):
        books = mgUtil.novel_find_by_user(json['member_id'],
                                          json['first'] if checker.key_exit('first') else False)
        if books:
            return netUtil.success(data=books)
        else:
            return netUtil.success()


# --------------------------------分割线-------------------------------- #

@app.route('/user/register', methods=['POST'])
def user_register():
    json = request.json
    tel = mgUtil.user_find_by_tel(json['tel'])
    if tel:
        return netUtil.fail(message='账号已存在')

    user = mgUtil.user_register(json)
    if user:
        return netUtil.success(message='注册成功', data=user)
    else:
        return netUtil.fail(message='注册失败')


@app.route('/user/login', methods=['POST'])
def user_login():
    json = request.json
    if not mgUtil.user_find_by_tel(json['tel']):
        return netUtil.fail(message='账号不存在')

    user = mgUtil.user_find_by_tel_psw(tel=json['tel'], psw=json['password'])
    if user:
        return netUtil.success(message='登陆成功', data=user)
    else:
        return netUtil.fail(message='账号密码出错')

# --------------------------------分割线-------------------------------- #
