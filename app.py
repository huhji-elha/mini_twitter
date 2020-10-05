
# mini_twitter app file

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

import jwt
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

# add git login authorize

'''
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
'''

def get_user(user_id) :
    user = current_app.database.execute(text("""
    SELECT
        id,
        name,
        email,
        profile
    FROM users
    WHERE id = user_id
    """) , {
        'user_id' : user_id
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


    # created_user = {
    #     'id' : row['id'],
    #     'name' : row['name'],
    #     'email' : row['email'],
    #     'profile' : row['profile']
    # } if row else None

    # return jsonify(created_user)

def get_timeline(user_id) :
    timeline = current_app.database.execute(text("""
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

    return [{
        'user_id' : tweet['user_id'],
        'tweet' : tweet['tweet']
    } for tweet in timeline]


def get_user_id_and_password(email) :
    row = current_app.database.execute(text("""
    SELECT
        id,
        hashed_password
    FROM users
    WHERE email = :email
    """), {'email' : email}).fetchone()
    
    return {
        'id' : row['id'],
        'hashed_password' : row['hashed_password']
    } if row else None

##### Decorators #####
def login_required(f) :
    @wraps(f)
    def decorated_function(*args, **kwargs) :
        access_token = request.headers.get('Authorization')
        if access_token is not None :
            try :
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError :
                payload = None
            if payload is None : return Response(status=401)
            user_id = payload['user_id']
            g.user_id = user_id 
            g.user = get_user(user_id) if user_id else None
        else :
            return Response(status=401)
        
        return f(*args, **kwargs)
    return decorated_function

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
        # new_user_id = app.database.execute(text("""
        #    INSERT INTO users (
        #        name,
        #        email,
        #        profile,
        #        hashed_password
        #     ) VALUES (
        #         :name,
        #         :email,
        #         :profile,
        #         :password
        #     )
        # """), new_user).lastrowid
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)

        return jsonify(new_user_info)
    
    @app.route("/login", methods=['POST'])
    def login() :
        credential = request.json
        email = credential['email']
        password = credential['password']
        user_credential = get_user_id_and_password(email)

        if user_credential and bcrypt.checkpw(password.encode('UTF-8'),
            user_credential['hashed_password'].encode('UTF-8')) :
            
            user_id = user_credential['id']
            payload = {
                'user_id' : user_id,
                'exp' : datetime.utcnow() + timdelta(seconds = 60 * 60 * 24)
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')

            return jsonify({
                'access_token' : token.decode('UTF-8')
            })
        else :
            return '', 401

    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet() :
        user_tweet = request.json
        user_tweet['id'] = g.user_id
        tweet = user_tweet['tweet']

        if len(tweet) > 300 :
            return "300자를 초과했습니다", 400
        insert_tweet(user_tweet)

        return '', 200

    @app.route("/follow", methods=['POST'])
    @login_required
    def follow() :
        payload = request.json
        payload['id'] = g.user_id
        insert_follow(payload)

        return '', 200

    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow() :
        payload = request.json
        payload['id'] = g.user_id
        insert_unfollow(payload)

        return '', 200

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id) :
        return jsonify({
            'user_id' : user_id,
            'timeline' : get_timeline(user_id)
        })

    return app

