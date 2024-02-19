# import uuid
# from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from models import StoreModel
from schemas import StoreSchema
# Blueprint is to divide api into a few segment


blp = Blueprint("Stores", "stores", description="Operations on stores")

# all to /store/string<store_id> will run below method
@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200,StoreSchema)
    def get(self,store_id):
           store = StoreModel.query.get_or_404(store_id)
           return store
        #  try:  
            
        #    return stores[store_id]
        #  except KeyError:

        #     abort(404,message="store not found")

    def delete(self,store_id):
           store = StoreModel.query.get_or_404(store_id)
           db.session.delete(store)
           db.session.commit()

           return {"Message":"store is deleted."}       
    

     # try:

        #     del stores[store_id]
            
        #     return {"message":" Store deleted"}
        
        # except KeyError:
             
        #      abort(404, message="Store not found")


@blp.route("/store")
class StoreList(MethodView):

    @blp.response(200,StoreSchema(many=True))
    def get(self):

        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(200,StoreSchema)
    def post(self,store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400,message="the name  already exist in database")
        except SQLAlchemyError:
            abort(500,message = "error arise when item insertion to database")
            
        return store

    
    # get the json from client
    #   store_data = request.get_json()

    # format validation
    #   if "name" not in store_data:
    #     abort(400, message="Bad request, name is absent")

    # duplication detection
    #   for store in stores.values():
    #     if(store_data["name"] == store["name"]):
    #         abort(400,message = "Store already exists")

    #   store_id = uuid.uuid4().hex
    #   new_store = {**store_data,"id":store_id}# unpack the dictionary to seperate parameters
    #   stores[store_id]= new_store
    # # new_store = {"name": store_data["name"], "items":[]}
    # # stores.append(new_store)
    #   return new_store, 201
