from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from crawl.matjip_to_db import populate_matjip_db
from datetime import datetime, timedelta

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.seoul_matjip





# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'apple'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt


import hashlib

datetime.now()

#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
   return render_template('main.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/date')
def date():
   return render_template('date.html')

@app.route('/board')
def board():
    return render_template('board.html')

@app.route('/cafe_Gyeonggido')
def cafe_Gyeonggido():
   return render_template('cafe_Gyeonggido.html')

@app.route('/cafe_Seoul')
def cafe_Seoul():
   return render_template('cafe_Seoul.html')

@app.route('/cafe')
def cafe():
   return render_template('cafe.html')

@app.route('/food_Gyeonggido')
def food_Gyeonggido():
   return render_template('food_Gyeonggido.html')

@app.route('/food_Seoul')
def food_Seoul():
   return render_template('food_Seoul.html')

@app.route('/food')
def food():
   return render_template('food.html')

@app.route('/play1')
def play1():
   return render_template('play1.html')

@app.route('/play4')
def play4():
   return render_template('play4.html')

@app.route('/play')
def play():
   return render_template('play.html')


@app.route('/play3')
def play3():
   return render_template('play3.html')


@app.route('/shop_Gyeonggido')
def shop_Gyeonggido():
   return render_template('shop_Gyeonggido.html')

@app.route('/shop_Seoul')
def shop_Seoul():
   return render_template('shop_Seoul.html')

@app.route('/shop')
def shop():
   return render_template('shop.html')

@app.route('/pick')
def pick():
   return render_template('pick.html')


#################################
##  맛집을 위한 API            ##
#################################
@app.route('/matjip', methods=["GET"])
def get_matjip():
    # gu_receive 라는 변수에 전달받은 구 이름을 저장합니다.
    gu_receive = request.args.get('gu_give')
    print("Gu received:", gu_receive)

    # 구 이름에 해당하는 모든 맛집 목록을 불러옵니다.
    matjip_list = list(db.user.find({'gu': gu_receive}, {'_id': False}))
    print("Matjip list:", matjip_list[:30])
    # matjip_list 라는 키 값에 맛집 목록을 담아 클라이언트에게 반환합니다.
    return jsonify({'result': 'success', 'matjip_list': matjip_list})





#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   nickname_receive = request.form['nickname_give']



   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   db.users.insert_one({'id':id_receive,'pw':pw_hash,'nick':nickname_receive})

   return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   print(id_receive, pw_receive)
   # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
   result = db.users.find_one({'id':id_receive,'pw':pw_hash})

   # 찾으면 JWT 토큰을 만들어 발급합니다.
   if result is not None:
      # JWT 토큰에는, payload와 시크릿키가 필요합니다.
      # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
      # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
      # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
      payload = {
         'id': id_receive,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)
      }
      token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

      # token을 줍니다.
      return jsonify({'result': 'success','token':token})
   # 찾지 못하면
   else:
      return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
   # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
   # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
   token_receive = request.headers['token_give']

   # try / catch 문?
   # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

   try:
      # token을 시크릿키로 디코딩합니다.
      # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      print(payload)

      # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
      # 여기에선 그 예로 닉네임을 보내주겠습니다.
      userinfo = db.users.find_one({'id':payload['id']},{'_id':0})
      return jsonify({'result': 'success','nickname':userinfo['nick']})
   except jwt.ExpiredSignatureError:
      # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
      return jsonify({'result': 'fail', 'msg':'로그인 시간이 만료되었습니다.'})


################### board 게시판############################

@app.route('/message', methods=["POST"])
def set_message():


    username_receive = request.form['username_receive']
    contents_receive = request.form['contents_receive']
    print(username_receive,contents_receive)
    
    doc = {
        'username': username_receive,
        'contents': contents_receive,
        'created_at': datetime.now()
    }
    print(doc,"db에 들어갈 내용임")
    db.messages.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '메시지 작성에 성공하였습니다!'})


@app.route('/message', methods=["GET"])
def get_messages():
    date_now = datetime.now()
    date_before = date_now - timedelta(days=1)
    messages = list(db.messages.find({'created_at': {
                    '$gte': date_before, '$lte': date_now}}, {'_id': False}).sort('created_at', -1))
    return jsonify({'result': 'success', 'messages': messages})

@app.route('/message/edit', methods=["POST"])
def edit_message():
    username_receive = request.form['username_give']
    contents_receive = request.form['contents_give']

    db.messages.update_one({'username': username_receive}, {
                           '$set': {'contents': contents_receive, 'created_at': datetime.now()}})

    return jsonify({'result': 'success', 'msg': '메시지 변경에 성공하였습니다!'})



if __name__ == '__main__':
   app.run('localhost',port=5502,debug=True)