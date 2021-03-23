from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from crawl.matjip_to_db import populate_matjip_db
from datetime import datetime, timedelta

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.seoul_matjip

SECRET_KEY = 'apple'

import jwt


import hashlib

datetime.now()

##  HTML   

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


##  맛집을 위한 API 

@app.route('/matjip', methods=["GET"])
def get_matjip():
    gu_receive = request.args.get('gu_give')
    print("Gu received:", gu_receive)

    matjip_list = list(db.user.find({'gu': gu_receive}, {'_id': False}))
    print("Matjip list:", matjip_list[:30])
    return jsonify({'result': 'success', 'matjip_list': matjip_list})


##  로그인을 위한 API 

@app.route('/api/register', methods=['POST'])
def api_register():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   nickname_receive = request.form['nickname_give']



   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   db.users.insert_one({'id':id_receive,'pw':pw_hash,'nick':nickname_receive})

   return jsonify({'result': 'success'})


# [로그인 API]

@app.route('/api/login', methods=['POST'])
def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   print(id_receive, pw_receive)
   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   result = db.users.find_one({'id':id_receive,'pw':pw_hash})

   if result is not None:
      payload = {
         'id': id_receive,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)
      }
      token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
      return jsonify({'result': 'success','token':token})
   else:
      return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
@app.route('/api/nick', methods=['GET'])
def api_valid():
   token_receive = request.headers['token_give']

   try:
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      print(payload)

      userinfo = db.users.find_one({'id':payload['id']},{'_id':0})
      return jsonify({'result': 'success','nickname':userinfo['nick']})
   except jwt.ExpiredSignatureError:
      return jsonify({'result': 'fail', 'msg':'로그인 시간이 만료되었습니다.'})


################### board 게시판###########################

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