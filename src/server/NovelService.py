from flask import Flask, request

from src.novel import DBNovel
from src.util import Checker
from src.util import NetUtil
from src.util import MongoUtil

app = Flask(__name__)
app.debug = True
checker = Checker.Checker()
mgUtil = MongoUtil.MongoUtil()
netUtil = NetUtil.NetUtil()
dbNovel = DBNovel.DBNovel()


@app.route('/test/', methods=['POST', 'GET'])
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


@app.route('/novel/my', methods=['POST', 'GET'])
def get_my_books():
    if request.method == 'POST':
        member_id = request.json['member_id']
        if checker.key_exit('first', request.json):
            first = request.json['first']
        else:
            first = False
    else:
        member_id = request.args.get('member_id')
        first = request.args.get('first') if (request.args.get('first') is not None) else False
    books = mgUtil.novel_find_by_user(int(member_id), first)
    if books:
        return netUtil.success(data={'books': books})
    else:
        return netUtil.success()


@app.route('/novel/detail', methods=['POST', 'GET'])
def query_novel():
    if request.method == 'POST':
        id = request.json['id']
    else:
        id = request.args.get('id')
    return netUtil.success(dbNovel.findNovel(id))


@app.route('/novel/chapter', methods=['POST', 'GET'])
def query_chapter():
    if request.method == 'POST':
        novelId = request.json['novel_id']
        chapterId = request.json['chapter_id']
    else:
        novelId = request.args.get('novel_id')
        chapterId = request.args.get('chapter_id')
    chapter = dbNovel.findChapter(novelId, chapterId)
    str = ''.join(chapter['chapters'][0]['content'])
    chapter['chapters'][0]['content'] = str
    return netUtil.success(chapter['chapters'][0]) if chapter is not None else netUtil.fail()


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


if __name__ == '__main__':
    app.run()
# --------------------------------分割线-------------------------------- #
