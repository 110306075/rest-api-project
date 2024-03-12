from flask import Flask,jsonify
from flask_smorest import Api

from db import db, rDB
import secrets
import models
import os
import redis

from dotenv import load_dotenv

from rq import Queue
from flask_jwt_extended import JWTManager

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


from flask_migrate import Migrate





def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    connection = redis.from_url(os.getenv("REDIS_URL"))



    app.queue = Queue("emails", connection=connection)
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)

    migrate = Migrate(app,db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "182959266477927998400120216293379711271"

 

    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def token_not_refresh_callback(jwt_header,jwt_payload):
        return(jsonify({"description":"The token is not fresh.",
                        "error": "fresh_token_required",}),
                        401,
                        )

    @jwt.token_in_blocklist_loader
    def check_token_in_blocklist(jwt_header,jwt_payload):
        jti = jwt_payload["jti"]
        token_in_redis = rDB.get(jti)
        return token_in_redis is not None
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return (jsonify({"description": "The token is unaviable",
                "error":"token_revoked"}),
                401,)



    @jwt.additional_claims_loader
    def add_claims(identity):
        if identity == 1:
            return{"is_admin": True}
        return{"is_admin": False}



    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)


    

    return app





