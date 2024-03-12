
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from db import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from models import StoreModel
from schemas import StoreSchema, ConditionSchema


blp = Blueprint("Stores", "stores", description="Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200,StoreSchema)
    def get(self,store_id):
           store = StoreModel.query.get_or_404(store_id)
           return store


    def delete(self,store_id):
           store = StoreModel.query.get_or_404(store_id)
           db.session.delete(store)
           db.session.commit()

           return {"Message":"store is deleted."}       
    


@blp.route("/store")
class StoreList(MethodView):

    @jwt_required()
    @blp.arguments(ConditionSchema)
    @blp.response(200,StoreSchema(many=True))
    def get(self,condition):
        con = "id"
        if  condition["condition"] is not None :
            con = condition["condition"]
        try:
            return StoreModel.query.order_by(getattr(StoreModel, con)).all()
        except SQLAlchemyError:
            abort(500,message = "invalid condition")
             
    
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


