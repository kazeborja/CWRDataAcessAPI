from flask.app import Flask
from flask.ext.cache import Cache
from flask.ext.track_usage import TrackUsage
from flask.ext.track_usage.storage.sql import SQLStorage
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/commonworks'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///commonworks.db'
app.config['TRACK_USAGE_USE_FREEGEOIP'] = False
app.config['TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'exclude'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
#cache = Cache(app, config={'CACHE_TYPE': 'memcached', 'CACHE_MEMCACHED_SERVERS': ['localhost:11211']})
app.config['DEBUG'] = True
db = SQLAlchemy(app)

from app import views

