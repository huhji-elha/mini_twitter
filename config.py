
from sqlalchemy import create_engine, text

db = {
        'user' : 'root',
        'password' : 'test1234',
        'host' : 'localhost',
        'port' : 0000,
        'database' : 'mini_twitter'
    }

db_url = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}?charset=utf8"
db = create_engine(db_url, encoding='utf-8', max_overflow = 0)


