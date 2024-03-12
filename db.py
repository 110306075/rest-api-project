from flask_sqlalchemy import SQLAlchemy
import redis
db = SQLAlchemy()





rDB = redis.Redis(
  host='redis-11878.c292.ap-southeast-1-1.ec2.cloud.redislabs.com',
  port=11878,
  password='kuIQ3tQPiE0cX8w7WZuNML9ejHc0ibcj')

