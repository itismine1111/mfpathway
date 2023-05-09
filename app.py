from ast import keyword
from sre_parse import State
import traceback
from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Flask
from flask import jsonify, make_response, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError
from passlib.hash import pbkdf2_sha256

# from app.nr_models import AutopartProduct
from app.nr_models import Banner, ImageUploads
from app.nr_models import Services, User, Faq, Blogs, find_value_by_slug, insert_number_in_slug, Category, Brand, \
    MakeModel
from helpers import generate_token_reset_password, verify_reset_token, email_notification, email_notification_for_contact_user,email_notification_for_setting_user
from helpers import save_image
from app.nr_models import State1
from app.nr_models import City
from app.nr_models import *
from app.nr_models import Add_attribute_to_category
from app.nr_models import Store_Product
from app.nr_models import Store_Address
from app.nr_models import Cms_Page

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app)
jwt = JWTManager(app)


def sluggify(item):
    return item.replace(" ", "-").lower()


def edit_message(status, collection):
    if status == 'A':
        return f"{collection} has been activated"
    elif status == 'I':
        return f"{collection} has been deactivated"
    else:
        return f"{collection} has been deleted"


@app.route("/")
def home():
    return {"message": "Welcome to the API"}


# =================Banner==============

@app.route("/admin/banner_add", methods=['POST'])
@jwt_required()
def banner_add():
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"banner/"
    image_path = save_image(request.files['image'], folder)
    banner = Banner(
        title=data["title"],
        description=data["description"],
        link=data['link'],
        image=image_path,
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    banner.save_to_db()
    return {
               "message": "created successfully",
               "status": True,
               "data": {
                   "title": data["title"],
                   "description": data["description"],
                   "image": image_path,
                   "link": data["link"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/banner_edit/<string:id>", methods=['PUT'])
@jwt_required()
def banner_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"banner/"
    if 'image' in request.files.keys():
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        banner = Banner.update_in_db(id, data)
        banner = Banner.find_by_id(id)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(banner.get_json()["status"],
                                    " Banner") if "status" in data.keys() else "Updated successfully",
            "data": banner.get_json(),
            "status": True
        }
    )), 200

@app.route("/admin/banner_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def banner_edit_by_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    
    status = request.get_json()["status"]
    
    try:
        banner = Banner.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(banner.get_json()["status"],
                                    " Banner"), # if "status" in status.keys() else "Updated successfully",
            "data": banner.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/banner_all", methods=['POST'])
@jwt_required()
def banner_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
        "message": "List of all banners",
        "data": Banner.retrieve_all_banners(limit, offset),
        "recordsTotal": len(Banner.retrieve_all_banners()),
        "draw": data["draw"] if 'draw' in data.keys() else None,
        "status": True
    }


@app.route("/admin/banner/<string:id>")
@jwt_required()
def banner_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        banner = Banner.find_by_id(id)
    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "Banner Details",
        "data": banner.get_json(),
        "status": True
    }

#===============================Find State and city and country ======================

@app.route("/admin/state/<int:country_id>")
@jwt_required()
def state_find_by_id(country_id):
    try:
        state = State1.find_state_by_country_id(country_id)
    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "state Details",
        "data": state,
        "recordsTotal": len(state),
        "status": True
    }


@app.route("/admin/city/<int:state_id>")
@jwt_required()
def city_find_by_id(state_id):
    try:
        city = City.find_city_by_state_id(state_id)
    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "City Details",
        "data": city,
        "recordsTotal": len(city),
        "status": True
    }


@app.route("/admin/all_countries",methods=["GET"])
def countries_all():
    try:
        return {
        "message": "List of all countries",
        "data":Countries.retrieve_all_countries(),
        "recordsTotal": len(Countries.retrieve_all_countries()),
        "status": True
    }
    except Exception as e:
            response = {"status": 'error', "message": f'{str(e)}'}
            return make_response(jsonify(response)), 200
# =========================Auth=========================

@app.route("/admin/register", methods=["POST"])
def register():
    data = request.get_json()
    roles=['admin', 'supplier', 'independent', 'manufacturer']
    pattern = re.compile('[a-zA-Z0-9\s]+$')

    user = User(
         _id=ObjectId(),
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=pbkdf2_sha256.hash(data['password']),
        phone_number=data['phone_number'],
        email_verified=True,
        select_subscription_type='Null',
        role=data['role'],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    if user.find_by_email(data['email']):
        return {"message": "Email already exists", "status": False}, 400

    elif user.find_by_username(data['username']):
        return {"message": "username already exists", "status": False}, 400

    elif user.find_by_phone_number(data['phone_number']):
        return {"message": "Phone Number already exists", "status": False}, 400

        

    try:
        if user.role in roles:
            if(pattern.search(user.username)!=None):                           
                user.save_to_db()
            else:
                return{
                    "message":"special character not allowed in username",
                    "status":False
                },400
        else:
            return {
                   "message": "Invalid role",
                   "status": False}, 400
    except ValidationError:
        return {
                   "message": "Invalid email",
                   "status": False}, 400
    user = user.find_by_email(data['email'])
    if user:
        return {
                   "data": user.get_json(),
                   "message": "User has been created",
                   "status": True
               }, 201
    return {
               "message": "An error occured from our side.",
               "status": False
           }, 500

@app.route("/admin/user/<string:id>")
@jwt_required()
def user_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        user = User.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "User Details",
               "data": user.get_json(),
               "status": True
           }, 200




@app.route("/admin/user_all/<string:role>", methods=['POST'])
@jwt_required()
def user_all(role):
    roles=['admin', 'supplier', 'independent', 'manufacturer']
    offset = None
    limit = None
    
    print(role)
    data = request.get_json()
    print(data)
    
    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
        
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    response ={
               "message": "List of all particular User",               
               "data": User.retrieve_all_user(limit, offset,role)if role in roles else None,
               "status": True,
               "recordsTotal": len(User.retrieve_all_user(role=role)),
               "draw": data["draw"] if 'draw' in data.keys() else None,
           }
    return make_response(jsonify(response)),200

@app.route("/admin/user_edit/<string:id>", methods=['PUT'])
@jwt_required()
def user_edit(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    token=request.headers.get('authorization')
    print(token)
    user = User.find_by_email(get_jwt_identity()) 
    print(user)
    if user==token:
        print(user)
    
    if user.find_by_email(data['email']):
        return {"message": "Email already exists", "status": False}, 400

    elif user.find_by_username(data['username']):
        return {"message": "username already exists", "status": False}, 400

    elif user.find_by_phone_number(data['phone_number']):
        return {"message": "Phone Number already exists", "status": False}, 400

    
    
    try:        

        user = User.update_in_db(id, data)
        user = User.find_by_id(id)
    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(user.get_json()["status"],
                                "User") if "status" in data.keys() else "Updated successfully",
        "data": user.get_json(),
        "status": True
    }



@app.route("/admin/user_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def user_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        user = User.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(user.get_json()["status"],
                                    "User"), # if "status" in status.keys() else "Updated successfully",
            "data": user.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/login", methods=['POST'])
def login():
    data = request.get_json()
    role=None
    
    if 'password' not in data.keys():
        return {
                   "message": "Password field is missing",
                   "status": False
               }, 404
    if 'email' not in data.keys():
        return {
                   "message": "Email field is missing",
                   "status": False
               }, 404

    user = User.find_by_email(email=data['email']) 
    
    if user and pbkdf2_sha256.verify(data['password'], user.password):
            if user.role=='admin':                
                access_token = create_access_token(user.email, expires_delta=timedelta(days=5))
                return {
                    "access_token": access_token,
                    "status": True,
                    "data": user.get_json()
                }
    return {
               "message": "Invalid credentials",
               "status": False
           }, 400


@app.route("/user_forgot", methods=['POST'])
def user_forgot():
    try:
        data = request.form
        user = User.find_by_email(email=data['email'])
        token = generate_token_reset_password(str(user.email))
        url = f"http://127.0.0.1:8080/token_validate/{token}"
        print(url)
        email_sent = email_notification(url, str(user.email))
        response = {"status": "true", "message": "email sent successfully"}
        return make_response(jsonify(response)), 200
    except:
        traceback.print_exc()
        response = {"status": "error", "message": "Invalid email"}
        return make_response(jsonify(response)), 200


@app.route("/token_validate/<token>")
def token_validate(token):
    try:
        validate_token = verify_reset_token(str(token))
        print(validate_token)
        if validate_token.get("message") == 'Signature has expired':
            response = {"status": "False", "token": "Token has expired", "email": validate_token.get("message")}
            return jsonify(response), 200
        else:
            response = {"status": "True", "message": "Validate successfully", "email": validate_token.get("message")}
            return jsonify(response), 200


    except Exception as e:
        traceback.print_exc()
        return "email does not exist in database"


@app.route("/confirm_password", methods=["POST"])
def confirm_password():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    user = User.find_by_email(email=email)
    try:

        if password == confirm_password:

            new_hashpassword = pbkdf2_sha256.hash(password)
            print(new_hashpassword, "new_password")
            user.password = new_hashpassword
            user.save_to_db()
            response = {"status": "True", "message": "New password alloted"}
            return make_response(jsonify(response)), 200
        else:
            response = {"status": "error", "message": "password mismatch"}
            return make_response(jsonify(response)), 200
    except:
        response = {"status": "error", "message": "email does not exist"}
        return make_response(jsonify(response))


@app.route("/admin/change_password", methods=['POST'])
@jwt_required()
def change_password(): 
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    password=request.get_json()["password"]
    confirm_password=request.get_json()["confirm_password"]
    user = User.find_by_email(get_jwt_identity())
    
    
    try:

         if password == confirm_password:

             new_hashpassword = pbkdf2_sha256.hash(password)
             print(new_hashpassword, "new_password")
             user.password = new_hashpassword
             user.save_to_db()
             response = {"status": "True", "message": "New password alloted"}
             return make_response(jsonify(response)), 200
         else:
             response = {"status": "error", "message": "password mismatch"}
             return make_response(jsonify(response)), 200
    except:
         response = {"status": "error", "message": "Password does not exist"}
         return make_response(jsonify(response))

# =============Services=====================


@app.route("/admin/services_add", methods=['POST'])
@jwt_required()
def services_add():
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"services/"
    image_path = save_image(request.files['image'], folder)
    slug = sluggify(data["name"])
    if find_value_by_slug("mw_services", slug):
        slug = insert_number_in_slug("mw_services", slug) if insert_number_in_slug("mw_services", slug) else slug

    services = Services(
        name=data["name"],
        image=image_path,
        description=data["description"],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        slug=slug
    )
    services.save_to_db()
    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "image": image_path,
                   "description": data["description"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/services_edit/<string:id>", methods=['PUT'])
@jwt_required()
def services_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"services/"
    if 'image' in request.files.keys():
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        services = Services.update_in_db(id, data)
        services = Services.find_by_id(id)
    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(services.get_json()["status"],
                                " Service") if "status" in data.keys() else "Updated successfully",
        "data": services.get_json(),
        "status": True
    }
@app.route("/admin/services_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def services_edit_by_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        services = Services.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(services.get_json()["status"],
                                    " services"), # if "status" in status.keys() else "Updated successfully",
            "data": services.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/services_all", methods=['POST'])
@jwt_required()
def services_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
               "message": "List of all Services",
               "data": Services.retrieve_all_services(limit, offset),
               "recordsTotal": len(Services.retrieve_all_services()),
               "draw": data["draw"] if 'draw' in data.keys() else None,
               "status": True
           }, 200


@app.route("/admin/services/<string:id>")
@jwt_required()
def services_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        services = Services.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "Services Details",
               "data": services.get_json(),
               "status": True
           }, 200


# ==========================FAQ====================

@app.route("/admin/faq_add", methods=['POST'])
@jwt_required()
def faq_add():
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401


    faq = Faq(
        question=data["question"],
        answer=data["answer"],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    faq.save_to_db()
    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "question": data["question"],
                   "answer": data["answer"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/faq_edit/<string:id>", methods=['PUT'])
@jwt_required()
def faq_edit(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        faq = Faq.update_in_db(id, data)
        faq = Faq.find_by_id(id)
    except:
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(faq.get_json()["status"],
                                " Faq") if "status" in data.keys() else "Updated successfully",
        "data": faq.get_json(),
        "status": True
    }

@app.route("/admin/faq_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def faq_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        faq = Faq.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(faq.get_json()["status"],
                                    " faq"), # if "status" in status.keys() else "Updated successfully",
            "data": faq.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/faq_all", methods=['POST'])
@jwt_required()
def faq_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
               "message": "List of all faq",
               "data": Faq.retrieve_all_faq(limit, offset),
               "status": True,
               "recordsTotal": len(Faq.retrieve_all_faq()),
               "draw": data["draw"] if 'draw' in data.keys() else None,
           }, 200


@app.route("/admin/faq/<string:id>")
@jwt_required()
def faq_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        faq = Faq.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "Faq Details",
        "data": faq.get_json(),
        "status": True
    }


# ==========Blogs================
@app.route("/admin/blogs_add", methods=['POST'])
@jwt_required()

def blogs_add():
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"blogs/"
    image_path = save_image(request.files['image'], folder)
    slug = sluggify(data["name"])
    if find_value_by_slug("mw_blogs", slug):
        slug = insert_number_in_slug("mw_blogs", slug) if insert_number_in_slug("mw_blogs", slug) else slug
    blog = Blogs(
        name=data["name"],
        description=data["description"],
        link=data["link"],
        image=image_path,
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        slug=slug
    )
    blog.save_to_db()
    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "description": data["description"],
                   "link": data["link"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/blog_edit/<string:id>", methods=['PUT'])
@jwt_required()
def blog_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    if 'image' in request.files.keys():
        folder = f"blogs/"
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        blog = Blogs.update_in_db(id, data)
        blog = Blogs.find_by_id(id)
    except:
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(blog.get_json()["status"],
                                " Blog") if "status" in data.keys() else "Updated successfully",
        "data": blog.get_json(),
        "status": True
    }

@app.route("/admin/blog_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def blog_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    
    status = request.get_json()["status"]
    
    try:
        blog = Blogs.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(blog.get_json()["status"],
                                    " blog"), # if "status" in status.keys() else "Updated successfully",
            "data": blog.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/blog_all", methods=['POST'])
@jwt_required()
def blog_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
        "message": "List of all Blogs",
        "data": Blogs.retrieve_all_blogs(limit, offset),
        "status": True,
        "recordsTotal": len(Blogs.retrieve_all_blogs()),
        "draw": data["draw"] if 'draw' in data.keys() else None,
    }


@app.route("/admin/blog/<string:id>")
@jwt_required()
def blog_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        blog = Blogs.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "blogs Details",
        "data": blog.get_json(),
        "status": True
    }

#===========================Product attribute=======================

@app.route("/admin/attribute_add", methods=['POST'])
@jwt_required()
def attribute_add():
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    attribute = Attribute(        
        name=data["name"],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    attribute.save_to_db()
    return {
               "message": "Attributes created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/attribute_edit/<string:id>", methods=['PUT'])
@jwt_required()
def attribute_edit(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        attribute = Attribute.update_in_db(id, data)
        attribute = Attribute.find_by_id(id)
    except:
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(attribute.get_json()["status"],
                                " Attribute") if "status" in data.keys() else "Updated successfully",
        "data": attribute.get_json(),
        "status": True
    }

@app.route("/admin/attribute_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def attribute_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        attribute = Attribute.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(attribute.get_json()["status"],
                                    " Attribute"), # if "status" in status.keys() else "Updated successfully",
            "data": attribute.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/attribute_all", methods=['POST'])
@jwt_required()
def attribute_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
               "message": "List of all Attribute",
               "data": Attribute.retrieve_all_attribute(limit, offset),
               "status": True,
               "recordsTotal": len(Attribute.retrieve_all_attribute()),
               "draw": data["draw"] if 'draw' in data.keys() else None,
           }, 200


@app.route("/admin/attribute/<string:id>")
@jwt_required()
def attribute_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        attribute = Attribute.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "Attribute Details",
        "data": attribute.get_json(),
        "status": True
    }



#============================ Color==================================

@app.route("/admin/color_add", methods=['POST'])
@jwt_required()
def color_add():
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    color = Color(
        name=data["name"],
        color_code=data["color_code"],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    color.save_to_db()
    return {
               "message": "Color created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "color_code": data["color_code"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/color_edit/<string:id>", methods=['PUT'])
@jwt_required()
def color_edit(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        color = Color.update_in_db(id, data)
        color = Color.find_by_id(id)
    except:
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(color.get_json()["status"],
                                " Color") if "status" in data.keys() else "Updated successfully",
        "data": color.get_json(),
        "status": True
    }

@app.route("/admin/color_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def color_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    
    status = request.get_json()["status"]
    
    try:
        color = Color.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(color.get_json()["status"],
                                    " Attribute"), # if "status" in status.keys() else "Updated successfully",
            "data": color.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/color_all", methods=['POST'])
@jwt_required()
def color_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
               "message": "List of all Color",
               "data": Color.retrieve_all_color(limit, offset),
               "status": True,
               "recordsTotal": len(Color.retrieve_all_color()),
               "draw": data["draw"] if 'draw' in data.keys() else None,
           }, 200


@app.route("/admin/color/<string:id>")
@jwt_required()
def color_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        color = Color.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "Color Details",
        "data": color.get_json(),
        "status": True
    }



# =================Sub Category ===========================

def subcategory_add(category_id: str):
    # took data from user
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    # saving the image in subcategory under uploads
    folder = f"subcategory/"
    # returns the relative path of the saved image
    image_path = save_image(request.files['image'], folder)
    # converting the title to slug
    slug = sluggify(data["title"])
    # checks whether the slug is unique
    if find_value_by_slug("mw_category", slug):
        # if not unique then insert number
        slug = insert_number_in_slug("mw_category", slug) if insert_number_in_slug("mw_category", slug) else slug

    # creating the sub category instance
    sub_category = Category(
        _id=ObjectId(),
        title=data['title'],
        image=image_path,
        description=data['description'],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        parent_id=category_id,
        slug=slug
    )

    # saving the changed category in the db
    sub_category.save_to_db()

    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "title": data["title"],
                   "image": image_path,
                   "description": data["description"],
                   "status": "A",
               }
           }, 200


# ==============Category====================#

@app.route("/admin/category_add", methods=['POST'])
@jwt_required()
def category_add():
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    if 'parent_id' in data.keys():
        return subcategory_add(data['parent_id'])

    folder = f"category/"
    image_path = save_image(request.files['image'], folder)
    slug = sluggify(data["title"])
    if find_value_by_slug("mw_category", slug):
        print(slug)
        slug = insert_number_in_slug("mw_category", slug) if insert_number_in_slug("mw_category", slug) else slug
        print(slug)
    category = Category(
        title=data['title'],
        image=image_path,
        description=data['description'],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        slug=slug
    )
    category.save_to_db()

    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "title": data["title"],
                   "image": image_path,
                   "description": data["description"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/category_edit/<string:id>", methods=['PUT'])
@jwt_required()

def category_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"category/"
    if 'image' in request.files.keys():
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        category = Category.update_in_db(id, data)
        category = Category.find_by_id(id)
    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(category.get_json()["status"],
                                " Category") if "status" in data.keys() else "Updated successfully",
        "data": category.get_json(category=True if category.parent_id == None else False),
        "status": True
    }
@app.route("/admin/category_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def category_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    status = request.get_json()["status"]
    
    try:
        category = Category.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(category.get_json()["status"],
                                    " category"), # if "status" in status.keys() else "Updated successfully",
            "data": category.get_json(),
            "status": True
        }
    )), 200


@app.route("/admin/category_all", methods=['POST'])
@jwt_required()
def category_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        offset = None
        limit = None
    children = ''
    try:
        children = bool(data['children'])
    except:
        children = False
    return {
        "message": "List of all Categories",
        "data": Category.retrieve_all_categories(limit, offset, children),
        "status": True,
        "recordsTotal": len(Category.retrieve_all_categories()),
        "draw": data["draw"] if 'draw' in data.keys() else None,
    }


@app.route("/admin/category/<string:id>", methods=['POST'])
@jwt_required()
def category_find_by_id(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        category = Category.find_by_id(id)


    except:
        traceback.print_exc()
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "Category Details",
               "data": category.get_json(children=data['children'] if 'children' in data.keys() else False,
                                         category=True if category.parent_id == None else False),
               "status": True
           }, 200

#Category Subcategory List

@app.route("/category_subcategory_all", methods=['POST'])

def frontend_category_subcategory_all():
    offset = None
    limit = None
    data = request.get_json()
   
    
    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        offset = None
        limit = None
    children = ''
    try:
        children = bool(data['children'])
    except:
        children = False
    
    list_of_categories=Category.retrieve_all_categories_subcategories()
    parent=list()
    for each in list_of_categories:
        
        del each["_id"] 
        del each["image"]
        del each["description"]
        del each["status"] 
        del each["created_at"]
        del each["updated_at"]
        del each["parent_id"] 
        each["text"]= each["title"]
        each["value"]=each["slug"]
        del each["title"]
        del each["slug"]
        child = list()
        for each_children in each["children"]:
            child.append({"text":each_children["title"],"value":each_children["slug"]})        
        each["children"]=child
    return {
        "message": "List of all Categories",
        "data": list_of_categories,
        "status": True,
        "recordsTotal": len(Category.retrieve_all_categories_subcategories()),
        "draw": data["draw"] if 'draw' in data.keys() else None,
    }


# ====================Product===================

@app.route("/admin/product_add", methods=['POST'])
@jwt_required()
def product_add():
    data = request.get_json()
    all_data=[]
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    slug = sluggify(data["name"])
    if find_value_by_slug("mw_autopart_product", slug):
        slug = insert_number_in_slug("mw_autopart_product", slug) if insert_number_in_slug("mw_autopart_product", slug) else slug
                                                                                               
    product = AutopartProduct(
            name=data['name'],
            program_name=data['program_name'],
            product_type=data['product_type'],
            product_link=data['product_link'],
            keywords=data['keywords'],
            sku=data['sku'],
            upc=data['upc'],
            isbn=data['isbn'],         
            condition=data['condition'],
            features=data['features'],
            warranty=data['warranty'],
            shipping_weight=data['shipping_weight'],
            image_ids=data['image_ids'],
            color_ids=data['color_ids'],
            description=data['description'],
            short_description=data['short_description'],          
            status='A',
            brand_id= data["brand_id"],
            model_id=data["model_id"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            subcategory_id=data["subcategory_id"],
            slug=slug
        )
    product.save_to_db()
    for i in data['product_specifications']:
        
        product_id=None
        with connect_to_db():
            product=[item for item in AutopartProduct.objects.filter()][-1]
            product_id=str(product._id)

        product_specification = ProductSpecification(
                product_id=product_id,
                attribute_id=i["attributeId"],
                category_attribute_relationship_id=i["attribute_to_category_id"],
                value=i["value"],               
                status='A',
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        
        product_specification.save_to_db()

        attribute=Attribute(
            name=i["attributeName"],
            status='A',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        attribute.save_to_db()
        all_data.append( {
                    
                    "product_id":product_id,
                    "attribute_id": i["attributeId"],
                    "category_attribute_relationship_id": i["attribute_to_category_id"],
                    "value": i["value"],
                    "attributeName":i["attributeName"],
                    "status": "A",
                })
    product = AutopartProduct.find_by_slug(slug)
    respose= {
                "message": "created successfully",
                "status": True,
                "data": {
                    "images": product.image_ids,
                    "color":product.color_ids,
                    "name": data["name"],
                    "program_name":data["program_name"],
                    "product_type":data["product_type"],
                    "product_link":data["product_link"],
                    "keywords":data['keywords'],
                    "sku":data['sku'],
                    "upc":data['upc'],
                    "isbn":data['isbn'],   
                    "features":data['features'],
               
                    "condition":data['condition'],
                    "warranty":data['warranty'],
                    "shipping_weight":data['shipping_weight'],
                    "description": data["description"],
                    "short description": data['short_description'],                 
                    "subcategory_id": data["subcategory_id"],
                    "model_id": data["model_id"],
                    "slug": slug,
                    "status": "A",
                    "brand_id": data["brand_id"],
                    "product_specifications":all_data,
                   
                }
            }
    
            
    return respose , 200


@app.route("/admin/product_edit/<string:id>", methods=['PUT'])
@jwt_required()
def product_edit(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())    
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    
    product=AutopartProduct.find_by_id(id)
    product_data={}
    for key in data.keys():
        if key!="product_specifications":
            product_data[key]=data[key]


    AutopartProduct.update_in_db(id,product_data)
    specifications=ProductSpecification.find_by_product_id(id)

    for specification in specifications:      
        new_specification=ProductSpecification(**specification)
     
        for data_specification in data["product_specifications"]:
            if (specification["_id"]==data_specification["_id"]):
                data_specification["product_id"]=data_specification["productId"]
                del data_specification["productId"]
                data_specification["attribute_id"]=data_specification["attributeId"]
                del data_specification["attributeId"]
                data_specification["category_attribute_relationship_id"]=data_specification["attribute_to_category_id"]
                del data_specification["attribute_to_category_id"],
                # del data_specification["attribute_to_category_id"],
                # del data_specification[""]
                new_specification.update_in_db(data_specification["_id"], data_specification)
    return {
        "message": edit_message(product_data.get_json()["status"],
                                 ) if "status" in data.keys() else "Updated successfully",
        #"data": product_data.get_json(),
        "status": True
    }

@app.route("/admin/product_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def product_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        product = AutopartProduct.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(product.get_json()["status"],
                                    " product"), # if "status" in status.keys() else "Updated successfully",
            "data": product.get_json(),
            "status": True
        }
    )), 200



@app.route("/admin/product_all", methods=['POST'])
@jwt_required()
def product_all():
    offset = None
    limit = None
    subcategory=None
    categories = None
    models = None
    model=None
    search_text = None
    brand=None
    brand_id=None
    model_id=None
    subcategory_id=None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    
    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        offset = None
        limit = None
    try:
        if 'categories' in data.keys():
            categories = data["categories"]
    except:
        categories = None
    try:
        if 'models' in data.keys():
            models = data["models"]
    except:
        models = None

    # Product search
 
    try:
        if 'search_text' in data.keys():
            search_text = data['search_text']
    except:
        search_text = None

    #Product search by filterBy and filterValue
    try:
        if data["filter_by"]=="brand" and "filter_value" in data.keys():
            brand=data["filter_value"]

    except:
        brand=None

    try:
        if data["filter_by"]=="category" and "filter_value" in data.keys():
            subcategory=data["filter_value"]
            
    except:
        subcategory=None
    try: 
        if data["filter_by"]=="model" and "filter_value" in data.keys():
            model=data["filter_value"]
    except:
        model=None
    
    #Product Advance Search

    if "brand_id"  in data.keys() :
            brand_id=data["brand_id"]
           
    else:
        brand_id=None
    if "model_id"  in data.keys() :
            model_id=data["model_id"]
           
    else:
        model_id=None
    if "subcategory_id" in data.keys():
        subcategory_id=data["subcategory_id"]
    
    return {
        "message": "List of all Products",
        "data": AutopartProduct.retrieve_all_products(limit, offset,categories,model_id=model_id, brand_id=brand_id, subcategory_id=subcategory_id, brand=brand,models=models,subcategory=subcategory,model=model,
                                                      search_text=search_text),
        "status": True,
        "recordsTotal": len(
            AutopartProduct.retrieve_all_products(categories=categories,model_id=model_id, brand_id=brand_id, subcategory_id=subcategory_id,brand=brand,models=models,subcategory=subcategory,model=model,search_text=search_text)),
        "draw": data["draw"] if 'draw' in data.keys() else None,
    }


@app.route("/admin/product/<string:id>", methods=['POST'])
@jwt_required()
def product_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        product = AutopartProduct.find_by_id(id)        
        specification=ProductSpecification.find_by_product_id(str(product._id))
    except:
        traceback.print_exc()
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "Products Details",
               "data": product.get_json(),
               "status": True
           }, 200



# ========================Model===================

@app.route("/admin/model_add/<string:brand_id>", methods=['POST'])
@jwt_required()
def model_add(brand_id: str):
    # took data from user
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    image_path=None
    folder = f"model/"
    image = request.files.get('image', None)
    if image:
        image_path = save_image(request.files['image'], folder)
    # saving the image in subcategory under uploads
    
 
    slug = sluggify(data["name"])
    # checks whether the slug is unique
    if find_value_by_slug("model", slug):
        # if not unique then insert number
        slug = insert_number_in_slug("model", slug) if insert_number_in_slug("model", slug) else slug

    # finding the category on which we will add subcategory
    brand = Brand.find_by_id(brand_id)
    # creating the sub category instance
    model = MakeModel(
        _id=ObjectId(),
        name=data['name'],
        image=image_path if image_path else None,
        description=data['description'],
        year=data['year'],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        parent=brand_id,
        slug=slug
    )

    # adding the subcategory in the found category
    brand.children.append(model)

    # saving the changed category in the db
    brand.save_to_db()

    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "image": image_path,
                   "description": data["description"],
                   "year": data["year"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/model_all/<string:brand_id>", methods=['POST'])
@jwt_required()
def model_all(brand_id):
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        offset = None
        limit = None
    brand = Brand.find_by_id(brand_id)
    return {
        "message": "List of all model in {}".format(brand.name),
        "data": brand.retrieve_all_model(limit, offset),
        "status": True,
        "recordsTotal": len(brand.retrieve_all_model(), ),
        "draw": data["draw"] if 'draw' in data.keys() else None,
    }


@app.route("/admin/model_edit/<string:id>", methods=['PUT'])
@jwt_required()
def model_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    folder = f"model/"
    if 'image' in request.files.keys():
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        model = Brand.update_model(id, data)
        model = Brand.find_by_model_id(id)

    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(model.get_json()["status"],
                                "  Model") if "status" in data.keys() else "Updated successfully",
        "data": model.get_json(),
        "status": True
    }

@app.route("/admin/model_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def model_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        #model = MakeModel.update_in_db_status(id, status)
        model = Brand.update_in_db_status(id, status)

    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(model.get_json()["status"],
                                    " product"), # if "status" in status.keys() else "Updated successfully",
            "data": model.get_json(),
            "status": True
        }
    )), 200



@app.route("/admin/model/<string:id>", methods=["POST"])
@jwt_required()

def model_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        model = Brand.find_by_model_id(id)


    except:
        traceback.print_exc()
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "model Details",
               "data": model.get_json(),
               "status": True
           }, 200

#=====================================Product Specification=====================================

@app.route("/admin/product_specification_add", methods=['POST'])
@jwt_required()
def product_specification_add():
    data = request.get_json()
    print(data)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    all_data=[]  
    
    for i in data:
        product_id=None
        with connect_to_db():
            product=[item for item in AutopartProduct.objects.filter()][-1]
            product_id=str(product._id)
  

        product_specification = ProductSpecification(
            product_id=product_id,
            attribute_id=i["attribute_id"],
            category_attribute_relationship_id=i["category_attribute_relationship_id"],
            value=i["value"],
            status='A',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        product_specification.save_to_db()
        all_data.append( {
                    
                    "product_id":product_id,
                    "attribute_id": i["attribute_id"],
                    "category_attribute_relationship_id": i["category_attribute_relationship_id"],
                    "value": i["value"],
                    "status": "A",
                })
    return {
               "message": "Product specification created successfully",
               "status": True,
               "data":all_data
               
           }, 200

@app.route("/admin/product_specification_edit/<string:id>", methods=['PUT'])
@jwt_required()
def product_specification_edit(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        product_specification = ProductSpecification.update_in_db(id, data)
        product_specification = ProductSpecification.find_by_id(id)
    except:
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(product_specification.get_json()["status"],
                                "Product Specification") if "status" in data.keys() else "Updated successfully",
        "data": product_specification.get_json(),
        "status": True
    }

# ==================Brand=====================

@app.route("/admin/brand_add", methods=['POST'])
@jwt_required()
def brand_add():
    data = request.form
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    image_path=None
    folder = f"brand/"
    image = request.files.get('image', None)
    if image:
        image_path = save_image(request.files['image'], folder)
    slug = sluggify(data["name"])
    if find_value_by_slug("mw_brand", slug):
        slug = insert_number_in_slug("mw_brand", slug) if insert_number_in_slug("mw_brand", slug) else slug

    brand = Brand(
        name=data['name'],
        image=image_path if image_path else None,
        description=data['description'],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        slug=slug
    )

    brand.save_to_db()

    return {
               "message": "created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "image": image_path if image_path else None,
                   "description": data["description"],
                   "status": "A",
               }
           }, 200


@app.route("/admin/brand_edit/<string:id>", methods=['PUT'])
@jwt_required()
def brand_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401


    folder = f"brand/"
    if 'image' in request.files.keys():
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        brand = Brand.update_in_db(id, data)
        brand = Brand.find_by_id(id)


    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(brand.get_json()["status"],
                                " Brand") if "status" in data.keys() else "Updated successfully",
        "data": brand.get_json(),
        "status": True
    }

@app.route("/admin/brand_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def brand_edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    status = request.get_json()["status"]
    
    try:
        brand = Brand.update_in_brand_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(brand.get_json()["status"],
                                    " brand"), # if "status" in status.keys() else "Updated successfully",
            "data": brand.get_json(),
            "status": True
        }
    )), 200



@app.route("/admin/brand_all", methods=['POST'])
@jwt_required()
def brand_all():
    offset = None
    limit = None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        offset = None
        limit = None
    children = ''
    try:
        children = bool(data['children'])
    except:
        children = False
    return {
        "message": "List of all Categories",
        "data": Brand.retrieve_all_brand(limit, offset, children),
        "status": True,
        "recordsTotal": len(Brand.retrieve_all_brand()),
        "draw": data["draw"] if 'draw' in data.keys() else None,
    }


@app.route("/admin/brand/<string:id>", methods=['POST'])
@jwt_required()
def brand_find_by_id(id):
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401


    try:
        brand = Brand.find_by_id(id)
    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "Brand Details",
               "data": brand.get_json(children=data['children'] if 'children' in data.keys() else False),
               "status": True
           }, 200
#################################add-attribute-to-cat################################
@app.route("/admin/attribute_to_cat_add",methods=["POST"])
@jwt_required()
def add_attribute_to_cat_add():
    data=request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    att_to_cat=Add_attribute_to_category(
        category_id=data["category_id"],
        attribute_id=data["attribute_id"],
        status='A',
        created_at=datetime.now(),
        updated_at="",
    )
    att_to_cat.save_to_db()
    return {
               "message": "Add_attribute_to_cat created successfully",
               "status": True,
               "data": {

                   "category_id": data["category_id"],
                   "attribute_id":data["attribute_id"],
                   "status": "A",
                   
               }
           }, 200
   
@app.route("/admin/attribute_to_cat_edit_status/<string:id>", methods=['PUT'])
@jwt_required()
def attribute_to_cat__edit_status(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    status = request.get_json()["status"]
    
    try:
        attribute_add_to_cat = Add_attribute_to_category.update_in_db_status(id, status)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(attribute_add_to_cat.get_json()["status"],
                                    " Attribute"), # if "status" in status.keys() else "Updated successfully",
            "data": attribute_add_to_cat.get_json(),
            "status": True
        }
    )), 200

@app.route("/admin/attribute_add_to_all", methods=['POST'])
@jwt_required()
def attribute_add_to_all():
    offset = None
    limit = None
    category_id=None
    data = request.get_json()
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])    
    except:
            offset=None
            limit=None

    try:
        if "category_id"   in data.keys() :
            category_id=data["category_id"]
           

    except:
        category_id=None
    return {
               "message": "List of all Attribute",
               "data": Add_attribute_to_category.retrieve_all_attribute_add_to_cat(limit, offset,category_id=category_id),
               "status": True,
               "recordsTotal": len(Add_attribute_to_category.retrieve_all_attribute_add_to_cat(category_id=category_id)),
               #"test": Add_attribute_to_category.retrieve_all_attribute_add_to_cat(limit, offset,category_id=category_id)[0],
               #"test2": ""
           }, 200

#attribute_add_to_cat update
@app.route("/admin/attribute_to_cat_edit/<string:id>", methods=['PUT'])
@jwt_required()
def add_attribute_cat_edit(id):
    data = dict(request.form)
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        add_attribute_cat = Add_attribute_to_category.update_in_db(id, data)
        add_attribute_cat = Add_attribute_to_category.find_by_id(id)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(add_attribute_cat.get_json()
                                    ) if "status" in data.keys() else "Updated successfully",
            #"data": add_attribute_cat.get_json(),
            "status": True
        }
    )), 200

#get_by_id
@app.route("/admin/attribute_to_cat_id/<string:id>")
@jwt_required()
def attribute_to_cat_find_by_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401

    try:
        attribute_cat = Add_attribute_to_category.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
        "message": "Attribute_to_cat Details",
        "data": attribute_cat.get_json(),
        "status": True
    }

##################################Contact_us###########################################
#contact_us add
@app.route("/admin/contact_us_add",methods=["POST"])
@jwt_required()
def contact_us_add():
    import socket   
    hostname = socket.gethostname() 
    data=request.get_json()
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    contact=Contact_us(
        name=data["name"],
        company_name=data["company_name"],
        email=data["email"],
        status='A',
        ip=socket.gethostbyname(hostname),
        msg=data["msg"],
        created_at=datetime.now()
        
    )
    contact.save_to_db()
    ab=Setting.retrieve_all_settings()
    for i in ab:
        abc=i["email"]
    print(abc)    

    a="Hello,\n"+"  " +data["name"]+"  "+"wants to communicate with you.\n"+"   "+"name:"+data["name"]+"\n"+"   "+"company_name:"+data["company_name"]+"\n"+"   "+"email:"+data["email"]+"\n"+"   "+"ip:"+socket.gethostbyname(hostname)+"\n"+"   "+"msg:"+data["msg"]
    email_sent = email_notification_for_setting_user(a,abc)
    
    return {
               "message": "contact_us created successfully",
               "status": True,
               "data": {

                   "name": data["name"],
                   "company_name":data["company_name"],
                   "email":data["email"],
                    "status":"A"
                   
               }
           }, 200


##################################################
#contact_us list
@app.route("/admin/contact_us_all", methods=['POST'])
@jwt_required()
def contact_us_all():
    offset = None
    limit = None
    data = request.get_json()
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except:
        return {"message": "limit and offset must be integer", "status": False}, 400
    return {
               "message": "List of all contact_us",
               "data": Contact_us.retrieve_all_contact_us(limit, offset),
               "status": True,
               "recordsTotal": len(Contact_us.retrieve_all_contact_us()),
              
           }, 200


#email_send_to_contact_user 
@app.route("/admin/email_to_contact_user",methods=["POST"])
@jwt_required()
def email_to_contact_user():
    try:
        data = request.form
        user = User.find_by_email(get_jwt_identity())
        if user.role!='admin':
            return{
            "msg":"Unauthorized access",
            "status":"false"
            },401
        user =data['email']
        subject=data["mail_subject"]
        a=data["mail_body"]
        print(type(user))
        email_sent = email_notification_for_contact_user(a,subject,str(user))
        response = {"status": "true", "message": "email sent successfully"}
        return make_response(jsonify(response)), 200
    except:
        traceback.print_exc()
        response = {"status": "error", "message": "Invalid email"}
        return make_response(jsonify(response)), 200

# =======================User Image=============================
@app.route("/admin/image_add", methods=['POST'])
@jwt_required()
def image_add_for_user():
    data = request.form
    user = User.find_by_email(get_jwt_identity())
    folder = f"product/"
    image_path = save_image(request.files['image'], folder)
    image = ImageUploads(
        _id=ObjectId(),
        type=data['type'] if 'type' in data.keys() else None,
        image=image_path,
        parent_id=str(user._id),
        is_thumbnail=data['is_thumbnail'] if '_thumbnail' in data.keys() else None,
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )        

    image.save_to_db()

    return {
               "message": "created successfully",
               "status": True,
               "data": {
                   "_id": str(image._id),
                   "type": data['type'] if 'type' in data.keys() else None,
                   "image": image_path,
                   "parent_id": str(user._id)
               }
           }, 200


@app.route("/admin/image_edit/<string:image_id>", methods=['PUT'])
def image_edit_by_id(image_id):
    data = dict(request.form)

    folder = f"product/"
    if 'image' in request.files.keys():
        image_path = save_image(request.files['image'], folder)
        data['image'] = image_path
    try:
        image = ImageUploads.update_in_db(image_id, data)

    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(image.get_json()["status"],
                                "  Image") if "status" in data.keys() else "Updated successfully",
        "data": image.get_json(),
        "status": True
    }


@app.route("/admin/image_all")
@jwt_required()
def all_image_by_userid():
    user = User.find_by_email(get_jwt_identity())
    return {
        "message": "List of all Images",
        "data": ImageUploads.retrieve_all_images(str(user._id)),
        "status": True,
        "recordsTotal": len(ImageUploads.retrieve_all_images(str(user._id)))
    }


# ==============================FRONTEND=========================

#------------------------------------User Authentication------------------------------------
#User Registration

@app.route("/register", methods=["POST"])
def frontend_register():
    data = request.get_json()
    roles=['supplier', 'independent', 'manufacturer']
    pattern = re.compile('[a-zA-Z0-9\s]+$')

    user = User(
         _id=ObjectId(),
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=pbkdf2_sha256.hash(data['password']),
        phone_number=data['phone_number'],
        email_verified=False,
        select_subscription_type='Null',
        role=data['role'],
        status='A',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    if user.find_by_email(data['email']):
        return {"message": "Email already exists", "status": False}, 400

    elif user.find_by_username(data['username']):
        return {"message": "username already exists", "status": False}, 400

    elif user.find_by_phone_number(data['phone_number']):
        return {"message": "Phone Number already exists", "status": False}, 400
    try:
        if user.role in roles: 
            if (pattern.search(user.username)!=None):                                          
                user.save_to_db()
            else:
                return{
                    "message":"special character not allowed in username",
                    "status":False
                },400

        else:
            return {
                   "message": "Invalid role",
                   "status": False}, 400
    except ValidationError:
        return {
                   "message": "Invalid email",
                   "status": False}, 400
    user = user.find_by_email(data['email'])
    if user:
        return {
                   "data": user.get_json(),
                   "message": "User has been created",
                   "status": True
               }, 201
    return {
               "message": "An error occured from our side.",
               "status": False
           }, 500

#Login

@app.route("/login", methods=['POST'])
def frontend_login():
    data = request.get_json()  
    
    if 'email' and 'password' not in data.keys():
        return {
                   "message": "please enter email and Password both",
                   "status": False
               }, 200
    if 'email' not in data.keys():
        return {
                   "message": "Email field is missing",
                   "status": False
               }, 200

    user = User.find_by_email(email=data['email']) 
    
    if user and pbkdf2_sha256.verify(data['password'], user.password):
            if user.role!='admin':                
                access_token = create_access_token(user.email, expires_delta=timedelta(days=5))
                return {
                    "access_token": access_token,
                    "status": True,
                    "data": user.get_json()
                }
    return {
               "message": "Invalid credentials",
               "status": False
           }, 200


#Change password

@app.route("/change_password", methods=['POST'])
@jwt_required()
def frontend_change_password(): 
    
    password=request.get_json()["password"]
    confirm_password=request.get_json()["confirm_password"]
    user = User.find_by_email(get_jwt_identity()) 
    
    try:
         if password == confirm_password:
             new_hashpassword = pbkdf2_sha256.hash(password)           
             user.password = new_hashpassword
             user.save_to_db()
             response = {"status": "True", "message": "New password alloted"}
             return make_response(jsonify(response)), 200
         else:
             response = {"status": "error", "message": "password mismatch"}
             return make_response(jsonify(response)), 200
    except:
         response = {"status": "error", "message": "Password does not exist"}
         return make_response(jsonify(response))

#User Edit

@app.route("/user_edit/<string:id>", methods=['PUT'])
@jwt_required()
def frontend_user_edit(id):
    data = request.get_json()
    
    if user.find_by_email(data['email']):
        return {"message": "Email already exists", "status": False}, 400

    elif user.find_by_username(data['username']):
        return {"message": "username already exists", "status": False}, 400

    elif user.find_by_phone_number(data['phone_number']):
        return {"message": "Phone Number already exists", "status": False}, 400


    try:        

        user = User.update_in_db(id, data)
        user = User.find_by_id(id)
    except:
        traceback.print_exc()
        return {"message": "Invalid id", "status": False}, 400

    return {
        "message": edit_message(user.get_json()["status"],
                                "User") if "status" in data.keys() else "Updated successfully",
        "data": user.get_json(),
        "status": True
    }




# ----------------------Banner-----------------------------------------
@app.route("/banner_all", methods=['GET'])
def frontend_banner_all():
    return {
        "message": " data retrieve successfully",
        "status": True,
        "recordsTotal": len(Banner.retrieve_all_banners(status='A')),
        "data": Banner.retrieve_all_banners(status='A')
    }


# ---------------------------------Services------------------------------

@app.route("/service_all", methods=['POST'])
def frontend_service_all():
    limit = None
    offset = None
    data = request.form
    try:
        if "offset" in data.keys():
            offset = int(data['offset'])
        if "limit" in data.keys():
            limit = int(data['limit'])
    except:
        traceback.print_exc()
        return {"mesage": "offset and limit should be integer", "status": False}, 400

    return {

        "data": Services.retrieve_all_services(limit, offset, status='A'),
        "recordsTotal": len(Services.retrieve_all_services(status='A')),
        "message": "List of all services",
        "status": True,
    }


@app.route("/service/<string:slug>")
def service_find_by_slug(slug):
    try:
        service = Services.find_by_slug(slug)


    except:
        return {"message": "slug doesnt exists", "status": False}, 400
    return {
        "message": "services Details",
        "data": service.get_json(),
        "status": True
    }


# --------------------------------FAQ----------------------------------

@app.route("/faq_all", methods=['GET'])
def frontend_faq_all():
    return {
        "data": Faq.retrieve_all_faq(status='A'),
        "recordsTotal": len(Faq.retrieve_all_faq(status='A')),
        "message": "List of FAQs",
        "status": True,
    }


# --------------------------------Blogs----------------------------------

@app.route("/blog_all", methods=['POST'])
def frontend_blog_all():
    limit = None
    offset = None
    data = request.form
    try:
        if "offset" in data.keys():
            offset = int(data['offset'])
        if "limit" in data.keys():
            limit = int(data['limit'])
        return {
            "data": Blogs.retrieve_all_blogs(limit, offset, status='A'),
            "recordsTotal": len(Blogs.retrieve_all_blogs(status='A')),
            "message": "List of all Blogs",
            "status": True
        }

    except:
        traceback.print_exc()
        return {
                   "message": "offset and limit shoulld be integer",
                   "status": True
               }, 200


@app.route("/blog/<string:slug>")
def blog_find_by_slug(slug):
    try:
        blog = Blogs.find_by_slug(slug)
    except:
        return {"message": "slug doesnt exists", "status": False}, 400
    return {
        "message": "blogs Details",
        "data": blog.get_json(),
        "status": True
    }


# ------------------------------------Category--------------------------------------------
@app.route("/category_all", methods=['GET'])
def frontend_category_all():
    try:
        return {
            "message": "List of all Categories",
            "data": Category.retrieve_all_categories(status='A', ),
            "status": True,
            "recordsTotal": len(Category.retrieve_all_categories(status='A'))
        }
    except Exception as e:
        traceback.print_exc()
        return "except"


@app.route("/category/<string:slug>")
def category_find_by_slug(slug):
    try:
        category = Category.find_by_slug(slug)
        response = {
                       "message": "category Details",
                       "data": category.get_json(children=True, category=True if category.parent_id == None else False),
                       "status": True
                   }, 200
        return response


    except Exception as e:
        traceback.print_exc()
        return {"message": "slug doesnt exists", "status": False}, 400


# --------------------------------------Brand---------------------------------------------
@app.route("/brand_all", methods=['POST'])
def frontend_brand_all():
    offset = None
    limit = None
    children = None
    data = request.get_json()
   
    try:
        offset = int(data["offset"])
    except:
        offset = None
    try:
        limit = int(data["limit"])
    except:
        traceback.print_exc()
        limit = None
    try:
        children = bool(data["children"])
    except:
        #traceback.print_exc()
        children = None
    
    list_of_brand=Brand.retrieve_all_brand(limit,offset,children)
    #print(children)

    for each in list_of_brand:
        del each["_id"] 
        
    return {
        "message": "List of all brands",
        "data": list_of_brand,
        "status": True,
        "recordsTotal": len(Brand.retrieve_all_brand(status='A'))
    }

@app.route("/brand/<string:slug>")
def brand_find_by_slug(slug):
    try:
        brand = Brand.find_by_slug(slug)

    except:
        return {"message": "slug doesnt exists", "status": False}, 400

    return {
        "message": "brand Details",
        "data": brand.get_json(status=True),
        "status": True
    }


# --------------------------------------Models ---------------------------------------------

@app.route("/model/<string:slug>")
def model_find_by_slug(slug):
    try:
        model = Brand.find_by_slug(slug)

    except:
        traceback.print_exc()
        return {"message": "slug doesnt exists", "status": False}, 400
    return {
               "message": "model Details",
               "data": model.get_json(),
               "status": True
           }, 200


# ---------------------------Product--------------------------

@app.route("/product_all", methods=['POST'])
def frontend_product_all():
    offset = None
    limit = None
    data = request.form
    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
        list_of_product=AutopartProduct.retrieve_all_products_list(limit,offset,status='A')
            
     
    except Exception as e:
            traceback.print_exc()
            response = {"status": 'error', "message": f'{str(e)}'}
            return make_response(jsonify(response)), 200
        
   
   
    return {
        "message": "List of all Products",
        "data": list_of_product,
        "status": True,
        
        "recordsTotal": len(
            AutopartProduct.retrieve_all_products_list(status='A'))
    },200


@app.route("/product/<string:slug>")
def product_find_by_slug(slug):
    try:
        product = AutopartProduct.find_by_slug(slug)
    except:
        return {"message": "slug doesnt exists", "status": False}, 400
    return {
               "message": "Products Details",
               "data": product.get_json(),
               "status": True
           }, 200

@app.route("/product_all/<string:subcategory_id>")
def product_find_by_subcategory_id(subcategory_id):
    try:
        product = AutopartProduct.find_by_subcategory_id(subcategory_id)

    except Exception as e:
            response = {"status": 'error', "message": f'{str(e)}'}
            return make_response(jsonify(response)), 200
    return {
        "message": "blogs Details",
        "data": product,
        "status": True
    }


@app.route("/get_year_by_model/<string:model_name>")
def get_year_by_model_name(model_name):
    return {
               "message": "List of Years",
               "data": Brand.find_by_model_name(model_name),
               "status": True
           }, 200


@app.route("/model_by_id/<string:id>")
def frontend_model_by_id(id):
    try:
        model = Brand.find_by_model_id(id)


    except:
        traceback.print_exc()
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "model Details",
               "data": model.get_json(children=True),
               "status": True
           }, 200

@app.route("/admin/setting_edit/<string:id>", methods=['PUT'])
@jwt_required()
def setting_edit(id):
    data = dict(request.form) 
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401


    try:
        setting = Setting.update_in_db(id, data)
        setting = Setting.find_by_id(id)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(setting.get_json()
                                    ) if "status" in data.keys() else "Updated successfully",
            "data": setting.get_json(),
            "status": True
        }
    )), 200

#get by id
@app.route("/admin/setting_id/<string:id>" , methods=['GET'])
@jwt_required()
def setting_id(id):
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401


    try:
        setting = Setting.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 200
    return {
               "message": "Settings Details",
               "data": setting.get_json(),
               "status": True
           }, 200

@app.route("/admin/setting_all",methods=['GET'])
@jwt_required()
def setting_all():
    #Takes only admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role!='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401


    return {
        "message": "List of all setting",
        "data": Setting.retrieve_all_settings(),
        "recordsTotal": len(Setting.retrieve_all_settings()),
        "status":True
    }

####################################Store-Address########################################
@app.route("/storeaddress_add",methods=["POST"])
@jwt_required()
def store_address_add():
    try:
        data = request.get_json()
        user = User.find_by_email(get_jwt_identity())
        if user.role=='admin':
            return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
        print(user)
        #return "hello"
        s_address=Store_Address(
            _id=ObjectId(),
            user_id=str(user._id),
            address=data["address"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            status='A',
            created_at=datetime.now(),
            updated_at=datetime.now()

            
            
        )
        s_address.save_to_db()
        #return "hello"
        return {
                "message": "store_address created successfully",
                "status": True,
                "data": {

                    
                        "address":data["address"],
                        "latitude":data["latitude"],
                        "status":'A',
                    
                }
            }, 200
    except Exception as e:
            response = {"status": 'error', "message": f'{str(e)}'}
            return make_response(jsonify(response)), 200

#store_address_list
@app.route("/store_address_list", methods=['POST'])
@jwt_required()
def store_add_list():
    offset = None
    limit = None
    user_id=None
    data = request.get_json()
    user = User.find_by_email(get_jwt_identity())
    if user.role=='admin':
            return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    try:
        if 'offset' in data.keys():
            offset = int(data["offset"])
        if 'limit' in data.keys():
            limit = int(data["limit"])
    except Exception as e:
        print(e)
        return {"message": "limit and offset must be integer", "status": False}, 400

    try:
        if "user_id"   in data.keys() :
            user_id=data["user_id"]
    except:
        user_id=None
    return {
               "message": "List of all store_address",
               "data": Store_Address.retrieve_all_product_address(limit, offset,user_id=user_id),
               "status": True,
               "recordsTotal": len(Store_Address.retrieve_all_product_address(user_id=user_id)),
              
           }, 200

####################################Store_Product####################################
@app.route("/storeproduct_add",methods=["POST"])
@jwt_required()
def store_product_add():
    data=request.get_json()
    try:
        user = User.find_by_email(get_jwt_identity())
        print(user)
        #takes other token exclude admin
   
        if user.role=='admin':
            return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
        product=AutopartProduct.find_by_slug(data["product_id"])
        if data["sale_price"] < data["regular_price"]: 
            s_product=Store_Product(
                    user_id=str(user._id),
                    color_ids=data["color_ids"],
                    product_id=str(product._id),
                    regular_price=data["regular_price"],
                    sale_price=data["sale_price"],
                    shipping=data["shipping"],
                    shipping_cost=data["shipping_cost"],
                    stock=data["stock"],
                    stock_quantity=data["stock_quantity"],
                    status='A',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                    
                )
            
            if Store_Product.find_by_product_id(data["product_id"]):
                return {"message": "data already exists just updated", "status": True}, 401
            else:
                s_product.save_to_db()
                
                return {
                    "msg":"data craeated successfully",
                    "status":True,
                    "data":{

                                #"user_id":user._id,
                                "color_id":s_product.color_ids,
                                "product_id":data["product_id"],
                                "regular_price":data["regular_price"],
                                "sale_price":data["sale_price"],
                                "status":'A',
                            
                        }

                }
        else:
            return {
                    "msg":"Regular price should gretter than sale_price",
                     "status":True
            },200
       
    except Exception as e:
            response = {"status": 'error', "message": f'{str(e)}'}
            return make_response(jsonify(response)), 200


    





 
#store_product_edit
@app.route("/storeproduct_edit/<string:id>", methods=['PUT'])
def p_edit(id):
    data = request.get_json()
    try:
        update = Store_Product.update_in_db(id, data)
        update = Store_Product.find_by_id(id)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(update.get_json()
                                    ) if "status" in data.keys() else "Updated successfully",
            "data": update.get_json(),
            "status": True
        }
    )), 200

#store_product list
@app.route("/my_product", methods=['POST'])
@jwt_required()
def my_product():
    offset = None
    limit = None
    data = request.get_json()
    #Not admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role=='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    else:
        try:
            if 'offset' in data.keys():
                offset= int(data["offset"])
                
            if 'limit' in data.keys():
                limit = int(data["limit"])
          
            user=Store_Product.find_by_user_id1(str(user._id),limit,offset)
        except  : 
            return {"message": "limit and offset must be integer", "status": False}, 400
        return {
                "message": "List of My Products",
                "data": user,
                "status": True,
                
            }, 200   

#store_product list
@app.route("/storeproduct_all", methods=['POST'])
@jwt_required()
def store_product_details():
    offset = None
    limit = None
    data = request.get_json()
    #Not admin token
    user = User.find_by_email(get_jwt_identity())
    if user.role=='admin':
        return{
            "msg":"Unauthorized access",
            "status":"false"
        },401
    else:
        try:
            if 'offset' in data.keys():
                offset= int(data["offset"])
                
            if 'limit' in data.keys():
                limit = int(data["limit"])
            # print(limit)  
            # print(offset)  
            #list_of_product=Store_Product.retrieve_all_store_product(limit,offset,status='A')
            user=Store_Product.find_by_user_id(str(user._id),limit,offset)
        except  : 
            return {"message": "limit and offset must be integer", "status": False}, 400
        return {
                "message": "List of all store_Product",
                "data": user,
                "status": True,
                
            }, 200  
####################################CMS_PAGE###########################################
@app.route("/cms_page",methods=["POST"])
def cms_add():
    data=request.get_json()
    cms=Cms_Page(
        title=data["title"],
        description=data["description"],
                    status='A',
                    created_at=datetime.now(),
                    updated_at=datetime.now()

    )
    cms.save_to_db()
    return "created"

#get by id
@app.route("/cms_id/<string:id>",methods=["GET"])
def cms_id(id):
   
    try:
        cms= Cms_Page.find_by_id(id)

    except:
        return {"message": "id doesnt exists", "status": False}, 400
    return {
               "message": "Cms Details",
               "data": cms.get_json(),
               "status": True
           }, 200
#cms update
@app.route("/cms_edit/<string:id>", methods=['PUT'])
def cms_edit(id):
    data = dict(request.form) 
    
    try:
        setting = Cms_Page.update_in_db(id, data)
        setting = Cms_Page.find_by_id(id)
    except:
        traceback.print_exc()
        return jsonify({"message": "Invalid id", "status": True}), 200

    return make_response(jsonify(
        {
            "message": edit_message(setting.get_json()
                                    ) if "status" in data.keys() else "Updated successfully",
            "data": setting.get_json(),
            "status": True
        }
    )), 200
#list
@app.route("/cms_all",methods=['GET'])
def cms_all():
    return {
        "message": "List of all cms_page",
        "data": Cms_Page.retrieve_all_cms_page(),
        "recordsTotal": len(Cms_Page.retrieve_all_cms_page()),
        "status":True
    }

if __name__ == '__main__':
    app.run(port=8080, debug=True)
