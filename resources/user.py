import os
from datetime import timedelta
from flask.views import MethodView
from flask import current_app
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256

from db import db, rDB
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from models import UserModel
from schemas import UserSchema, UserRegisterSchema, ConditionSchema
from flask_jwt_extended import create_access_token, get_jwt, jwt_required,create_refresh_token,get_jwt_identity


import requests
from task import send_user_registration_email
blp = Blueprint("Users", "users", description="Operations on users")
ACCESS_EXPIRES = timedelta(hours=1)


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self,user_data):
        if(UserModel.query.filter(or_(UserModel.username == user_data["username"])
                                                    
                                  )
                                  ).first():
            abort(409, message = "the user with the name or email is already exist")

        user = UserModel(username = user_data["username"],
                         email = user_data["email"],
                         password = pbkdf2_sha256.hash(user_data["password"]))
        
        db.session.add(user)
        db.session.commit()
        # rDB.set('test', 'well')
        
        current_app.queue.enqueue(send_user_registration_email,user.email,user.username)
        
        # send_simple_message(
        #     to = user.email,
        #     subject="Successfully signed up",
        #     body=f"Hi{user.username}, you have successfully signed up"

        # )


        return {"message": "user registered successfully"}, 201




@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]
            ).first()
        if user and pbkdf2_sha256.verify(user_data["password"],user.password):
            access_token = create_access_token(identity= user.id, fresh= True)
            # the client use it only access refresh endpoint
            refresh_token = create_refresh_token(identity=user.id)

            return{"access_token":access_token,"refresh_token":refresh_token}
        
        abort(401, message = "Invalid credentials")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh= True)
    def post(self):
        curremt_user = get_jwt_identity()
        new_token = create_access_token(identity=curremt_user, fresh=False)
        jti =get_jwt()["jti"]
        # BLockList.add(jti)
        rDB.set(jti, "",ex= ACCESS_EXPIRES)
        return{"access_token": new_token}




@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        rDB.set(jti,"",ex= ACCESS_EXPIRES)
        # BLockList.add(jti)
        return{"message":"logout successfully"}


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200,UserSchema)
    def get(self,user_id):
        user  = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message":"user is deleted"}, 200
    
@blp.route("/user")
class UserList(MethodView):
    @jwt_required()
    @blp.arguments(ConditionSchema)
    @blp.response(200,UserSchema(many= True))
    def get(self,condition):

        con = "id"
        if  condition["condition"] is not None :
            con = condition["condition"]
        try:
            return UserModel.query.order_by(getattr(UserModel, con)).all()
        except SQLAlchemyError:
            abort(500,message = "invalid condition input")
      
    

    

    








