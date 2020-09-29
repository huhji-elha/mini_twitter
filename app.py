
# mini_twitter app file

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

# access token
import bcrypt

# set을 JSON 형태로 변경하기 위한 JSON encoder. 
# set을 list로 변경함으로써 JSON으로 문제없이 변경될 수 있도록 한다.
class CustomJSONEncoder(JSONEncoder) :
    def default(self, obj) : # JSONEncoder의 default 메서드를 확장한다.
        if isinstance(obj, set) :# Json으로 변경하고자 하는 obj가 set인 경우
            return list(obj) # list로 변환하여 리턴한다.
        
        return JSONEncoder.default(self, obj)


# 이후 atomic 연산 추가 필요해! 이렇게 요청하는 new_user마다 id_count를 부여해버리면 HTTP 요청이 동시 요청될 경우
# id가 잘못 할당될 수 있다. 이러한 문제를 예방하기 위해 한 번에 한 스레드만 값을 증가시킬 수 있도록 하는 
# atomic increment operation을 사용해야 한다.



def sign_up() :
    new_user = request.json
    new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'),
            bcrypt.gensalt()
            )
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

def get_user(user_id) :
    user = current_app.database.execute(text("""
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
    return {
        'id' : user['id'],
        'name' : user['name'],
        'email' : user['email'],
        'profile' : user['profile']
    } if user else None

def insert_user(user) :
    return current_app.database.execute(text("""
    INSERT INTO users (
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
    """), user).lastrowid

def insert_tweet(user_tweet) :
    return current_app.database.execute(text("""
    INSERT INTO tweets (
        user_id,
        tweet
    )VALUES (
        :id,
        :tweet
    )
    """), user_tweet()).rowcount


def insert_follow(user_follow) :
    return current_app.database.execute(text("""
    INSERT INTO users_follow_list (
        user_id,
        follow_user_id
    )VALUES (
        :id,
        :follow
    )
    """), user_follow).rowcount

def insert_unfollow(user_unfollow) :
    return current_app.database.execute(text("""
    DELETE FROM users_follow_list
    WHERE user_id = :id
    AND follow_user_id = :unfollow
    """), user_unfollow).rowcount


    created_user = {
        'id' : row['id'],
        'name' : row['name'],
        'email' : row['email'],
        'profile' : row['profile']
    } if row else None

    return jsonify(created_user)

def get_timeline(user_id) :
    timeline = current_app.database.execute(text("""
    SELECT
        t.user_id,
        t.tweet
    FROM tweets t
    LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
    WHERE t.user_id = :user_id
    OR t.user_id = ufl.follow_user_id
    )""", {
        'user_id' : user_id
    }).fetchall()

    return [{
        'user_id' : tweet['user_id'],
        'tweet' : tweet['tweet']
    } for tweet in timeline]


def create_app(test_config = None) :
    app = Flask(__name__)
    
    # Flask의 default Json Encoder로 지정해준다.
    app.json_encoder = CustomJSONEncoder

    if test_config is None :
        app.config.from_pyfile("config.py")
    else :
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping() :
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up() :
        new_user = request.json
        new_user['password'] = bcrypt.hashpw(
            new_user['password'].encode('UTF-8'),
            bcrypt.gensalt()
        )
        new_user_id = app.database.execute(text("""
           INSERT INTO users (
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
        #new_user_id = insert_user(new_user)
        new_user_info = get_user(new_user_id)

        return jsonify(new_user_info)
    
    @app.route("/tweet", methods=['POST'])
    def tweet() :
        user_tweet = request.json
        tweet = user_tweet['tweet']

        if len(tweet) > 300 :
            return "300자를 초과했습니다", 400
        insert_tweet(user_tweet)

        return '', 200

    @app.route("/follow", methods=['POST'])
    def follow() :
        payload = request.json
        insert_follow(payload)

        return '', 200

    @app.route("/unfollow", methods=['POST'])
    def unfollow() :
        payload = request.json
        insert_unfollow(payload)

        return '', 200

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id) :
        return jsonify({
            'user_id' : user_id,
            'timeline' : get_timeline(user_id)
        })

    return app

