from flask import Blueprint, request
from flask.views import MethodView

from app.nr_models import User
from datetime import datetime

from mongoengine.errors import ValidationError

from flask_cors import cross_origin

from passlib.hash import pbkdf2_sha256

from helpers import GenerateApiToken

admin_auth = Blueprint('admin', __name__)

class fn_Register_View(MethodView):
    @cross_origin()
    def post(self):
        data = request.get_json()
        user = User(
            username=data['username'],
            first_name = data['first_name'],
            last_name=data['last_name'], 
            email=data['email'],
            password= pbkdf2_sha256.hash(data['password']),
            email_verified=False, 
            status='A',
            created_at=datetime.now(), 
            updated_at=datetime.now()
        )
    
        if user.find_by_email(data['email']):
            return {"msg":"Email already exists", "status":False}, 400
        try:
            user.save_to_db()
        except ValidationError:
            return {
                "msg":"Invalid email",
                "status":False}, 400
        user =user.find_by_email(data['email'])
        if user:
            return {
                "data":user.get_json(),
                "msg":"User has been created",
                "status":False
            }, 201
        return {
            "msg":"An error occured from our side.", 
            "status":False
        }, 500


class fn_Login_View(MethodView):
    @cross_origin()
    def post(self):
        data = request.get_json()
        if 'password' not in data.keys():
            return {"msg":"Password field is missing"}, 404
        if 'email' not in data.keys():
            return {"msg":"Email field is missing"}, 404
    
        user = User.find_by_email(email = data['email'])
    
        if user and pbkdf2_sha256.verify(data['password'], user.password):
            create_token = GenerateApiToken(str(user.id), data['password'])
            return {
                "access_token":create_token.generate_token(str(user.id), data['password']),
            }

        return {"msg":"Credentials entered is invalid"}, 400



class fn_LogOut_View(MethodView):
    pass


# # # Creating View Function/Resources
fn_Register_View = fn_Register_View.as_view('fn_Register_View')
fn_Login_View = fn_Login_View.as_view('fn_Login_View')
fn_LogOut_View = fn_LogOut_View.as_view('fn_LogOut_View')

# # # adding routes to the Views we just created
admin_auth.add_url_rule('/admin/register', view_func=fn_Register_View, methods=['POST'])
admin_auth.add_url_rule('/admin/login', view_func=fn_Login_View, methods=['POST'])
admin_auth.add_url_rule('/admin/logout', view_func=fn_Register_View, methods=['POST'])
