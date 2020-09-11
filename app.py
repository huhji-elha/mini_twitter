
# mini_twitter app file

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

def create_app(test_config = None) :
    app = Flask(__name__)

    if test_config is None :
        app.config.from_pyfile("config.py")
    else :
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database
    return app

# app start!
#app = Flask(__name__)
app.users = {}
app.id_count = 1
app.tweets = []

# set을 JSON 형태로 변경하기 위한 JSON encoder. 
# set을 list로 변경함으로써 JSON으로 문제없이 변경될 수 있도록 한다.
class CustomJSONEncoder(JSONEncoder) :
    def default(self, obj) : # JSONEncoder의 default 메서드를 확장한다.
        if isinstance(obj, set) :# Json으로 변경하고자 하는 obj가 set인 경우
            return list(obj) # list로 변환하여 리턴한다.
        
        return JSONEncoder.default(self, obj)

# Flask의 default Json Encoder로 지정해준다.
app.json_encoder = CustomJSONEncoder


@app.route("/ping", methods=['GET'])
def ping() :
    return "pong"

"""
이후 atomic 연산 추가 필요해! 이렇게 요청하는 new_user마다 id_count를 부여해버리면 HTTP 요청이 동시 요청될 경우
id가 잘못 할당될 수 있다. 이러한 문제를 예방하기 위해 한 번에 한 스레드만 값을 증가시킬 수 있도록 하는 
atomic increment operation을 사용해야 한다.
"""


@app.route("/sign-up", methods=['POST'])

"""
def sign_up() :
    new_user = request.json # 요청한 정보를 json으로 변환, new_user = {"id":1, "name":huhji} 상태.
    new_user["id"] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

    return jsonify(new_user) 
"""

def sign_up() :
    new_user = request.json
    new_user_id = app.database.execute(text("""
    INSERT INTO users(
        name,
        email,
        profile,
        hashed_password
    ) VALUES (
        :name,
        :email,
        :profile,
        :password
    )
    """), new_user).lastrowid

    row = current_app.database.execute(text("""
    SELECT
        id,
        name,
        email,
        profile
    FROM users
    WHERE id = new_user_id
    """) , {
        'user_id' : new_user_id
    }).fetchone()

    created_user = {
        'id' : row['id'],
        'name' : row['name'],
        'email' : row['email'],
        'profile' : row['profile']
    } if row else None

    return jsonify(created_user)


# tweet code
app.tweets = []

@app.route("/tweet", methods=['POST'])

"""
def tweet() :
    tweet_get = request.json
    user_id = int(tweet_get['id'])
    tweet = tweet_get['tweet']

    if user_id not in app.users :
        return "사용자가 존재하지 않습니다.", 400
    if len(tweet) > 300 :
        return "300자를 초과했습니다", 400

    user_id = int(tweet_get['id'])
    app.tweets.append({
        'user_id' : user_id,
        'tweet' : tweet
        })

    return '', 200
"""

def tweet() :
    user_tweet = request.json
    tweet = user_tweet['tweet']

    if len(tweet) > 300 :
        return '300자를 초과했습니다.'

    app.database.execute(text( """
    INSERT INTO tweets (
    user_id,
    tweet
    ) VALUES (
    :user_id,
    :tweet
    )
    """ ), user_tweet)

    return '', 200




@app.route("/follow", methods=['POST'])
def follow() :
    tweet_get = request.json
    user_id = int(tweet_get['id'])
    user_id_to_follow = int(tweet_get['follow'])

    if user_id not in app.users or user_id_to_follow not in app.users :
        return "사용자가 존재하지 않습니다.", 400
    user = app.users[user_id]
    # 해당 사용자가 팔로우하는 id를 모아놓기 위해 set을 사용한다.
    user.setdefault('follow', set()).add(user_id_to_follow)

    return jsonify(user)
    

@app.route("/unfollow", methods=['POST'])
def unfollow() :
    tweet_get = request.json
    user_id = int(tweet_get['id'])
    #왜 user_id_to_unfollow를 사용하지 않지? 메모리 절약을 위해?
    user_id_to_follow = int(tweet_get['unfollow'])

    if user_id not in app.users or user_id_to_follow not in app.users :
        return "사용자가 존재하지 않습니다.", 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow)

    return jsonify(user)

@app.route("/timeline/<int:user_id>", methods=['POST'])

"""
def timeline(user_id) :
    if user_id not in app.users :
        return "사용자가 존재하지 않습니다.", 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
        'user_id' : user_id,
        'timeline' : timeline
        })

"""

def timeline(user_id) :
    rows = app.database.execute(text("""
    SELECT
        t.user_id,
        t.tweet
    FROM tweets t
    LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
    WHERE t.user_id = :user_id
    OR t.user_id = ufl.follow_user_id
    """), {
        'user_id' : user_id
    }).fetchall()

    timeline = [{
        'user_id' : row['user_id'],
        'tweet' : row['tweet']
    } for row in rows]

    return jsonify({
        'user_id' : user_id,
        'timeline' : timeline
    })
