from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from models import StoreModel ,ItemModel , TagModel  
# from models.tag import TagModel
from schemas import TagSchema, TagItemSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)


        return store.tags.all()
    @blp.arguments(TagSchema)
    @blp.response(200,TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400,message = "the tag name has already exist in the store")
        tag = TagModel(**tag_data, store_id = store_id)


        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e :
            abort(500,message = str(e))
        
        return tag

# @blp.route("/tag/<string:tag_id>")
# class Tag(MethodView):
#     @blp.response(200,TagSchema)
#     def get(self, tag_id):
#      tag = TagModel.query.get_or_404(tag_id)

#      return tag
    


@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagToItem(MethodView):
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):

        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
          
          db.session.add(item)
          db.session.commit()

        except SQLAlchemyError:
            abort(500,message="error occur when inserting tags")
        
        return tag
    
    @blp.response(200,TagItemSchema)
    def delete(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
          
          db.session.add(item)
          db.session.commit()

        except SQLAlchemyError:
            abort(500,message="error occur when deleting tags")
        
        return{"message": "Item remove successfully from tag","item":item,"tag":tag}
    

@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200,TagSchema)
    def get(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    def delete(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag is deleted"}
        

        abort(400,message="can not delete tag, there is item associate with the tag")


        
        




                   