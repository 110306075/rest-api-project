from flask import Flask,jsonify
from flask_smorest import Api

from db import db
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

from blocklist import BLockList

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

    # is going to sign the jwt that 
    # the api knows this jwt is made by this api

    jwt = JWTManager(app)

    @jwt.needs_fresh_token_loader
    def token_not_refresh_callback(jwt_header,jwt_payload):
        return(jsonify({"description":"The token is not fresh.",
                        "error": "fresh_token_required",}),
                        401,
                        )

    @jwt.token_in_blocklist_loader
    def check_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLockList
    
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
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)


    

    return app





# stores =[
#     {

#         "name" : "My store",
#         "items" :[
#             {
#                 "name" :"Chair",
#                   "price" : 15
#                   }
#                   ]
#                   }

# ]
# store ={}

# items ={
# 1:{ "name":"CHair",
# "price": 17.99
# },
# 2: {"name":"Table",
#    "price":199
# }
#    }


# @app.get("/store") # http://127.0.0.1:5000/store
# def get_store_all():
#     # return "Hollo"

#     return{"store":list(stores.values())}

# # # Note JSON
# # # json is a long string that abide by a specific foramt including string numbers booleans and sub-object
# # # so that the client can understand what is inside
# # {
# #     "key": "Value",
# #     "another": 25.
# #     "List":[
# #         1,
# #         2,
# #         3,
# #     ],
# #     "obj":{
# #     "name":"Rolf",
# #     "age":25
# # }
# # }
# # in top-level everything must inside a list or a object
# # JSON(text that deliver over the Internet) is like a stringified python dictionary

# # automated testing and manual exploratory test (Insomnia client)
# # # creat store

# @app.post("/store")
# def create_store():
#     # get the json from client
#     store_data = request.get_json()

#     # format validation
#     if "name" not in store_data:
#         abort(400, message="Bad request, name is absent")

#     # duplication detection
#     for store in stores.values():
#         if(store_data["name"] == store["name"]):
#             abort(400,message = "Store already exists")

#     store_id = uuid.uuid4().hex
#     new_store = {**store_data,"id":store_id}# unpack the dictionary to seperate parameters
#     stores[store_id]= new_store
#     # new_store = {"name": store_data["name"], "items":[]}
#     # stores.append(new_store)
#     return new_store, 201

# # # create items in store

# @app.post("/item")
# def create_item():
#     item_data = request.get_json()# get req from client

#     # input format ensurance

#     if("price" not in item_data
#        or "store_id" not in item_data
#        or "name" not in item_data):
        
#         abort(400, message="Bad request, input not completed")

#     # duplication detection   
        
#     for item in items.values():
#         if(item_data["name"] == item["name"]
#            and item_data["store_id"]==item["store_id"]):
            
#             abort(400, message="Item already exists.")
    
#     # validatation
            
#     if  item_data["store_id"] not in stores:
         
#          abort(404,message="store not found")
#         # return {"message" : "Store not found"},404 

#     item_id = uuid.uuid4().hex
#     item = {**item_data, "id":item_id}
#     items[item_id] = item
#     # for store in stores:
#     #     if(store["name"] == name):
#     #      new_item = {"name": request_data["name"],"price": request_data["price"]}
#     #      store["items"].append(new_item)
#     return item, 201
#     # return{"message": "store not found"} , 404 

# @app.get("/item")
# def get_all_items():
#  return {"items":list(items.values())}

# # get store and items
# # get individual storex
# @app.get("/store/<string:store_id>")
# def get_store(store_id):  

#     # for store in stores:
#     #     if(store["name"] == name):
#      try:   
#          return stores[store_id]
#      except KeyError:
#                  abort(404,message="store not found")


# @app.get("/item/<string:item_id>")
# def get_item(item_id):
#     try:
#      return items[item_id]
#     except KeyError:
#         abort(404,message="item not found")
        

#     # for store in stores:
#     #     if(store["name"] == name):
         
#     #      return {"items": store["items"]}
#     # return{"message": "store not found"} , 404
        
# @app.delete("/item/<string:item_id>")
# def delete_item(item_id):
#         try:
#             del items[item_id]
#             return {"message":" Item deleted"}
#         except KeyError:
#             abort(404, message="Item not found")

# @app.put("/item/<string:item_id>")
# def update_item(item_id):
#     item_data = request.get_json()
#     if "price" not in item_data or "name" not in item_data:
#         abort(400, messa ="BAD request input is not completed")
#     try:
#         item = items[item_id]
#         item |= item_data # | is to replace the element in the specific dict

#         return item
#     except KeyError:
#         abort(404, message = "Item not found")


# @app.delete("/store/<string:store_id>")
# def delete_store(store_id):
#         try:
#             del stores[store_id]
#             return {"message":" Store deleted"}
#         except KeyError:
#             abort(404, message="Store not found")