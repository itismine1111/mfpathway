from ast import keyword
from email.policy import default
from pyexpat import model
import re
from datetime import datetime
from unicodedata import category


from setuptools import Require

from bson.objectid import ObjectId
# if error change it to from helpers import connect_to_db
from helpers import connect_to_db
from mongoengine import (
    StringField,
    Document,
    DateTimeField,
    EmailField,
    BooleanField,
    ObjectIdField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    FloatField,
    IntField
)
from bson.json_util import dumps
from mongoengine.errors import DoesNotExist
from mongoengine.queryset.visitor import Q

# if error change it to from helpers import connect_to_db
from helpers import connect_to_db


# Non schema based models

class Banner(Document):
    _id = ObjectIdField()
    title = StringField(required=True, max_length=128)
    description = StringField(required=True)
    image = StringField(required=True, max_length=255)
    link = StringField(required=True, max_length=255)
    status = StringField(required=True, max_length=1)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_banners'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "image": self.image,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def retrieve_all_banners(cls, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json() for item in cls.objects(status='A')]
            else:
                return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        banner = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key != "slug":
                    banner[key] = data[key]
            return banner.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        banner = cls.find_by_id(id)
        with connect_to_db():
            banner.status=status
            return banner.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))


class User(Document):
    _id = ObjectIdField()
    username = StringField(required=True, max_length=128)
    first_name = StringField(required=True, max_length=255)
    last_name = StringField(required=True, max_length=255)
    email = EmailField(required=True)
    email_verified = BooleanField()
    password = StringField()
    phone_number=StringField(required=True)
    select_subscription_type=StringField(required=True)
    role=StringField()
    status = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_users'}

    def save_to_db(self):
        with connect_to_db():
            self.save()
            
    @classmethod
    def find_by_id(cls, id, status='D'):
        with connect_to_db():
            if status=='A':
                return cls.objects(status='A').get(_id=ObjectId(id))
            else:
                return cls.objects(status__ne='D').get(_id=ObjectId(id))


    def get_json(self):
        return {
             '_id': str(self._id),
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'email_verified': self.email_verified,
            'phone_number':self.phone_number,
            'select_subscription_type':self.select_subscription_type,
            'role':self.role,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    

    @classmethod
    def update_in_db(cls, id, data):
        user = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key != 'username' and key != "role" and key!= 'password':
                    user[key] = data[key]
                user['updated_at'] = datetime.now()
                
            return user.save()



    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=id)

    @classmethod
    def update_in_db_status(cls, id, status):
        user = cls.find_by_id(id)
        with connect_to_db():
            user.status=status
            return user.save()

    @classmethod
    def retrieve_all_user(cls, limit=None, skip=None, role=None, status='D'):
        with connect_to_db():
            if role=='admin':
                print(role,"---")
                return [item.get_json() for item in cls.objects(status='A').filter(role='admin').skip(skip).limit(limit)]
            elif role=='supplier':
                return [item.get_json() for item in cls.objects(status='A').filter(role='supplier').skip(skip).limit(limit)]
            elif role=='independent':
                return [item.get_json() for item in cls.objects(status='A').filter(role='independent').skip(skip).limit(limit)]
            else:                              
                return [item.get_json() for item in cls.objects(status='A').filter(role='manufacturer').skip(skip).limit(limit)]
            

    
    @classmethod
    def find_by_id(cls, id, status='D'):
        with connect_to_db():
            if status=='A':
                return cls.objects(status='A').get(_id=ObjectId(id))
            else:
                return cls.objects(status__ne='D').get(_id=ObjectId(id))

        

    @classmethod
    def find_by_email(cls, email):
        with connect_to_db():
            try:
                return cls.objects.get(email=email)
            except DoesNotExist:
                return None

    @classmethod
    def find_by_username(cls, username):
        with connect_to_db():
            try:
                return cls.objects.get(username=username)
            except DoesNotExist:
                return 
                
    @classmethod
    def find_by_phone_number(cls, phone_number):
        with connect_to_db():
            try:
                return cls.objects.get(phone_number=phone_number)
            except DoesNotExist:
                return None

class Services(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=128)
    image = StringField(required=True, max_length=255)
    slug = StringField(required=True, max_length=128, unique=True)
    description = StringField(required=True)
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_services'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "image": self.image,
            "description": self.description,
            "slug": self.slug,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def retrieve_all_services(cls, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json() for item in cls.objects(status='A').skip(skip).limit(limit)]
            else:
                return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        services = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key != 'link' or key != "slug":
                    services[key] = data[key]
                services['updated_at'] = datetime.now()
            return services.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        services = cls.find_by_id(id)
        with connect_to_db():
            services.status=status
            return services.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def find_by_slug(cls, slug):
        with connect_to_db():
            return cls.objects.get(slug=slug)


class Faq(Document):
    _id = ObjectIdField()
    question = StringField(required=True)
    answer = StringField(required=True)
    status = StringField(required=True, max_length=1)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_faq'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "question": self.question,
            "answer": self.answer,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def retrieve_all_faq(cls, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json() for item in cls.objects(status='A')]
            else:
                return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        faq = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key != 'link':
                    faq[key] = data[key]
                faq['updated_at'] = datetime.now()
            return faq.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        faq = cls.find_by_id(id)
        with connect_to_db():
            faq.status=status
            return faq.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    

class Blogs(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=128)
    link = StringField(required=True, max_length=255)
    image = StringField(required=True, max_length=255)
    slug = StringField(required=True, max_length=128, unique=True)
    description = StringField(required=True)
    status = StringField(required=True, max_length=1)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_blogs'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "link": self.link,
            "image": self.image,
            "slug": self.slug,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def retrieve_all_blogs(cls, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json() for item in cls.objects(status='A').skip(skip).limit(limit)]
            else:
                return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        blogs = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key != "slug":
                    blogs[key] = data[key]
                blogs['updated_at'] = datetime.now()
            return blogs.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        blogs = cls.find_by_id(id)
        with connect_to_db():
            blogs.status=status
            return blogs.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def find_by_slug(cls, slug):
        with connect_to_db():
            return cls.objects.get(slug=slug)

# Product Attribute

class Attribute(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=256)    
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_attributes'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "name": self.name,           
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def retrieve_all_attribute(cls, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json() for item in cls.objects(status='A')]
            else:
                return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        attribute = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key != "slug":
                    attribute[key] = data[key]
            return attribute.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        attribute = cls.find_by_id(id)
        with connect_to_db():
            attribute.status=status
            return attribute.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))



# Color 

class Color(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=256)    
    color_code=StringField(required=True, max_length=256)
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'mw_colors'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "color_code": self.color_code,           
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def retrieve_all_color(cls, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json() for item in cls.objects(status='A')]
            else:
                return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        color = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key != "slug":
                    color[key] = data[key]
            return color.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        color = cls.find_by_id(id)
        with connect_to_db():
            color.status=status
            return color.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def find_by_color_ids(cls, color_id):
        with connect_to_db():
            print("List of ids",color_id)
            return [cls.objects.get(_id=ObjectId(id)) for id in color_id]




# schema based models

class Category(Document):
    _id = ObjectIdField()
    title = StringField(required=True, max_length=100)
    image = StringField(required=True)
    description = StringField(required=True)
    status = StringField(required=True, max_length=10)
    slug = StringField(required=True, max_length=128)
    parent_id = StringField()
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {"collection": "mw_category"}

    def save_to_db(self):
        '''
        This method can be used both by category and subcategory to save the the documents
        '''

        with connect_to_db():
            self.save()

    @classmethod
    def update_in_db(cls, id, data):
        '''
        This method is used to update both category and subcategory
        '''
        category = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key != "slug":
                    category[key] = data[key]
                category['updated_at'] = datetime.now()
            return category.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        category = cls.find_by_id(id)
        with connect_to_db():
            category.status=status
            return category.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def retrieve_all_categories(cls, limit=None, skip=None, children=False, status='D'):
        with connect_to_db():
            if status == 'A':
                data = []
                for item in cls.objects.filter(Q(status='A') & Q(parent_id=None)).skip(skip).limit(limit):
                    data.append(item.get_json(children, True, status=status))
                return data
            else:
                data = []
                for item in cls.objects.filter(Q(status__ne='D') & Q(parent_id=None)).skip(skip).limit(limit):
                    data.append(item.get_json(children, True, status=status))
                return data

    @classmethod
    def retrieve_all_subcategories(cls, category_id, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                data = []
                for item in cls.objects.filter(Q(status='A') & Q(parent_id__ne=None)):
                    if item.parent_id == str(category_id):
                        data.append(item.get_json(False, False))
                return data
            else:
                data = []
                for item in cls.objects.filter(Q(status__ne='D') & Q(parent_id__ne=None)):
                    if item.parent_id == str(category_id):
                        data.append(item.get_json(False, False))
                return data

    def get_json(self, children=False, category=True, status='D'):
        return {
            "_id": str(self._id),
            "title": self.title,
            "image": self.image,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "slug": self.slug,
            "parent_id": None if category else self.parent_id,
            "children": self.retrieve_all_subcategories(self._id, status) if children and category else None
        }

    @classmethod
    def find_by_slug(cls, slug):
        with connect_to_db():
            return cls.objects.get(slug=slug)


class MakeModel(EmbeddedDocument):
    _id = ObjectIdField()

    name = StringField(required=True, max_length=100)
    image = StringField()
    description = StringField(required=True)
    status = StringField(required=True, max_length=10)
    slug = StringField(required=True, max_length=128)
    parent = StringField(required=True)  # Brand
    year = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    def get_json(self, children=False):
        return {
            "_id": str(self._id),
            "name": self.name,
            "image": self.image,
            "description": self.description,
            "status": self.status,
            "slug": self.slug,
            "parent": self.parent,
            "year": self.year,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def update_in_db_status(cls, id, status):
        brand = cls.find_by_id(id)
        with connect_to_db():
            brand.status=status
            return brand.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))


class Brand(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=100)
    image = StringField()
    slug = StringField(required=True, max_length=128, unique=True)
    description = StringField(required=True)
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    children = ListField(EmbeddedDocumentField(MakeModel))

    meta = {"collection": "mw_brand"}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self, children=False, status='D'):

        return {
            "_id": str(self._id),
            "name": self.name,
            "image": self.image,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "slug": self.slug,
            "children": self.retrieve_all_model(status=status) if children else None
        }

    @classmethod
    def retrieve_all_brand(cls, limit=None, skip=None, children=False, status='D'):
        with connect_to_db():
            if status == 'A':
                return [item.get_json(children, status=status) for item in
                        cls.objects.filter(status='A').skip(skip).limit(limit)]
            else:
                return [item.get_json(children, status=status) for item in
                        cls.objects.filter(status__ne='D').skip(skip).limit(limit)]



    def retrieve_all_model(self, limit=None, skip=None, status='D'):
        with connect_to_db():
            if status == 'A':
                model_list = []
                if skip is None:
                    skip = 0
                if limit is None:
                    limit = len(self.children)
                for item in self.children[skip:skip + limit]:
                    if item.status == 'A':
                        model_list.append(item.get_json())
                return model_list
            else:
                model_list = []
                if skip is None:
                    skip = 0
                if limit is None:
                    limit = len(self.children)
                for item in self.children[skip:skip + limit]:
                    if item.status != 'D':
                        model_list.append(item.get_json())
                return model_list

    @classmethod
    def update_in_db(cls, id, data):
        brand = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key != "slug":
                    brand[key] = data[key]
            return brand.save()

# update brand status
    @classmethod
    def update_in_brand_status(cls, id, status):
        brand = cls.find_by_id(id)
        with connect_to_db():
            brand.status=status
            return brand.save()

    

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def find_by_model_id(cls, id):
        with connect_to_db() as connection:
            collection = connection.get_database('MYPAFWAY')["mw_brand"]
            brand = Brand(**collection.find_one({"children._id": ObjectId(id)}))
            for make_model in brand.children:
                if make_model._id == ObjectId(id):
                    return make_model
            return None

    @classmethod
    def find_by_model_name(cls, name):
        with connect_to_db() as connection:
            years = []
            collection = connection.get_database('MYPAFWAY')["mw_brand"]
            brand = Brand(**collection.find_one({"children.name": name}))
            for make_model in brand.children:
                if make_model.name == name:
                    years.append(make_model.year)
            return years

    @classmethod
    def find_by_model_slug(cls, slug):
        with connect_to_db() as connection:
            collection = connection.get_database('MYPAFWAY')["mw_brand"]
            brand = Brand(**collection.find_one({"children.slug": slug}))
            for make_model in brand.children:
                if make_model.slug == slug:
                    return make_model
            return None

    @classmethod
    def update_model(cls, id, data):
        with connect_to_db() as connection:
            collection = connection.get_database('MYPAFWAY')["mw_brand"]
            brand = Brand(**collection.find_one({"children._id": ObjectId(id)}))
            for make_model in brand.children:
                if make_model._id == ObjectId(id):
                    for key in data.keys():

                        if key != "created_at" and key != "updated_at" and key != "slug":
                            make_model[key] = data[key]
                    return brand.save()


# Update model status
    @classmethod
    def update_in_db_status(cls, id, status):
        with connect_to_db() as connection:
            collection = connection.get_database('MYPAFWAY')["mw_brand"]
            brand = Brand(**collection.find_one({"children._id": ObjectId(id)}))
            for make_model in brand.children:
                if make_model._id == ObjectId(id):
                    make_model.status = status
                    return brand.save()


 

    @classmethod
    def find_by_slug(cls, slug):
        with connect_to_db():
            return cls.objects.get(slug=slug)


# extra collections just because frontend wanted it
class AutopartProduct(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=128)
    program_name=StringField(required=True)
    product_type=StringField(required=True)
    product_link=StringField(required=True)
    keywords=StringField(required=True)
    sku=StringField(required=True)
    upc=StringField(required=True)
    isbn=StringField(required=True)    
    condition=StringField(required=True)
    warranty=StringField(required=True)
    shipping_weight=StringField(required=True)
    short_description = StringField(requried=True)
    description = StringField(required=True)
    thumb_image = StringField(required=True)
    status = StringField(requried=True)
    slug = StringField(required=True, max_length=128)
    created_at = DateTimeField(requried=True)
    updated_at = DateTimeField(required=True)
    thumb_image = StringField()    
    image_ids = ListField(StringField())
    brand_id=StringField()
    subcategory_id = StringField(required=True)
    model_id = StringField(required=True)
    color_ids = ListField(StringField())

  

    meta = {
        "collection": "mw_autopart_product",
        'indexes': [
            {
                'fields': ['$name'],
                'default_language': 'english',
                'weights': {'name': 2}
            }
        ]
    }

    def get_json(self):
        sub_category = Category.find_by_id(self.subcategory_id)
        model = Brand.find_by_model_id(self.model_id)
        brand = Brand.find_by_id(self.brand_id)
        image_path = ImageUploads.find_by_ids(self.image_ids)
        colors=Color.find_by_color_ids(self.color_ids)
        
        print(colors,"colorss")
        # for each in colors:
        #     print("coloerssssssssssssssssssssssss",each.to_json())
            
        
        thumbnail_path = ImageUploads.find_by_id(self.thumb_image) if self.thumb_image else None
        return {
            "_id": str(self._id),
            "name": self.name,
            "program_name":self.program_name,
            "product_type":self.product_type,
            'product_link':self.product_link,
            "keywords":self.keywords,
            "sku":self.sku,
            "upc":self.upc,
            "isbn":self.isbn,          
            "condition":self.condition,
            "warranty":self.warranty,
            "shipping_weight":self.shipping_weight,
            "description": self.description,                
            "short_description": self.short_description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "slug": self.slug,
            "subcategory_id": self.subcategory_id,
            "subcategory_name": sub_category.title,
            "subcategory_slug": sub_category.slug,
            "model_id": self.model_id,
            "brand_id": str(brand._id),
            "model_name":model.name,       
            "model_slug": model.slug,
            "thumb_image": {"_id":self.image_ids[0] if not self.thumb_image else self.thumb_image ,
                        "image": [image["image"] for image in image_path][0] if not self.thumb_image else thumbnail_path.image} ,
            "image_ids": [{"_id":i,"image":j} for i,j in zip(self.image_ids,[image["image"] for image in image_path])],
            "color_ids": [{"_id":i} for i in self.color_ids],
            

        }

        
    def save_to_db(self):
        with connect_to_db():
            return self.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    

    @classmethod
    def update_in_db(cls, id, data):
        product = cls.find_by_id(id)
        with connect_to_db():

            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key != "slug":
                    product[key] = data[key]
            product['updated_at'] = datetime.now()
            return product.save()

    @classmethod
    def update_in_db_status(cls, id, status):
        product = cls.find_by_id(id)
        with connect_to_db():
            product.status=status
            return product.save()


    @classmethod
    def retrieve_all_products(cls, limit=None, skip=None,categories=None,brand=None,models=None,subcategory=None,model=None,search_text=None):
        all_product = list()
        filter = Q(status__ne='D')
        if categories:
            filter = filter & Q(subcategory_id__in=categories)

        if models:
            filter = filter & Q(model_id__in=models)

        if model:
            filter = filter & Q(model_id=model)

        if brand:
            filter = filter & Q(brand_id=brand)

        if subcategory:
            filter = filter & Q(subcategory_id=subcategory)
        
        

        if search_text:
            regex = re.compile(f'.*{search_text}.*')
            filter = filter & Q(name=regex)
        with connect_to_db():
            for item in cls.objects.filter(filter).skip(skip).limit(limit):
                print(item.get_json())
                all_product.append(item.get_json())
            
            return all_product
            #return [item.get_json() for item in cls.objects.filter(filter).skip(skip).limit(limit)]

    @classmethod
    def retrieve_products_by_model_id(cls, model_id, skip=None, limit=None):
        with connect_to_db():
            return [item.get_json() for item in cls.objects.filter(model_id=model_id).skip(skip).limit(limit)]
    
    @classmethod
    def retrieve_all_products_list(cls, limit=None, skip=None):
        print(limit,skip)
        with connect_to_db():
            return [item.get_json() for item in cls.objects().skip(skip).limit(limit)]
    
    @classmethod
    def find_by_subcategory_id(cls,subcategory_id):
        with connect_to_db():
            return [item.get_json() for item in cls.objects.filter(subcategory_id=subcategory_id)]
    

    @classmethod
    def find_by_slug(cls, slug):
        with connect_to_db():
            return cls.objects.get(slug=slug)


# extra collections just because frontend wanted it

class ImageUploads(Document):
    _id = ObjectIdField()
    type = StringField()
    image = StringField(required=True)
    parent_id = StringField()
    is_thumbnail=StringField()
    is_active = BooleanField(default=False)
    status = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {
        "collection": "mw_uploads",
    }

    def get_json(self):
        return {
            "_id": str(self._id),
            "type": self.type,
            "image": self.image,
            "is_thumbnail":self.is_thumbnail,
            "parent_id": self.parent_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def save_to_db(self):
        with connect_to_db():
            self.save()

    @classmethod
    def retrieve_all_images(cls, parent_id, limit=None, skip=None):
        with connect_to_db():
            return [item.get_json() for item in
                    cls.objects.filter(Q(status='A') & Q(parent_id=parent_id)).skip(skip).limit(limit)]

    @classmethod
    def find_by_parent_id(cls, id):
        with connect_to_db():
            return [item._id for item in cls.objects.filter(parent_id=id)]

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))
    
    @classmethod
    def find_by_ids(cls, ids):
        with connect_to_db():
            print("List of ids",ids)
            return [cls.objects.get(_id=ObjectId(id)) for id in ids]

    @classmethod
    def find_by_ids(cls, ids):
        with connect_to_db():
            return [cls.objects.get(_id=ObjectId(id)) for id in ids]

    # TODO: tobe checked
    @classmethod
    def update_in_db(cls, id, data):
        image = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key != "type":
                    image[key] = data[key]
                image['updated_at'] = datetime.now()
            return image.save()


class State1(Document):
    _id=IntField()
    name=StringField(required=True, max_length=255)    
    country_id=IntField()
   

    meta = {
        "collection": "mw_state",
    }

    def get_json(self):
        return {
            "_id":self._id,
            "name":self.name,            
            "country_id": self.country_id,            
            
        }
    @classmethod
    def find_state_by_country_id(cls, country_id):
        with connect_to_db():
            return [item.get_json() for item in cls.objects.filter(country_id=country_id)]

class City(Document):
    _id=IntField()
    name=StringField(required=True, max_length=255)    
    state_id=IntField()
   

    meta = {
        "collection": "mw_city",
    }

    def get_json(self):
        return {
            "_id":self._id,
            "name":self.name,            
            "state_id": self.state_id,            
            
        }
    @classmethod
    def find_city_by_state_id(cls, state_id):
        with connect_to_db():
            return [item.get_json() for item in cls.objects.filter(state_id=state_id)]


class Countries(Document):
    _id=IntField()
    sortname=StringField()
    name=StringField()
    meta = {'collection': 'mw_country'}

    


    def get_json(self):
        return {
            "_id":self._id,
            "sortname": self.sortname,
            "name":self.name
            }
    @classmethod
    def retrieve_all_countries(cls):
        with connect_to_db():

            return [item.get_json() for item in cls.objects()]

def find_value_by_slug(collection_name, slug_value):
    with connect_to_db() as connection:
        key_list = ["mw_services", "mw_blogs", "mw_category", "mw_autopart_product", "mw_brand", "model"]
        if collection_name in key_list:

            if collection_name == "model":
                collection = connection.get_database('MYPAFWAY')["mw_brand"]
                return collection.find_one({"children.slug": slug_value})
            else:
                collection = connection.get_database('MYPAFWAY')[collection_name]
                return collection.find_one({"slug": slug_value})
        return None


def insert_number_in_slug(key, slug_value):
    with connect_to_db() as connection:
        key_list = ["mw_services", "mw_blogs", "mw_category", "mw_autopart_product", "mw_brand", "model"]
        if key in key_list:
            if key == "model":
                collection = connection.get_database('MYPAFWAY')["mw_brand"]
            else:
                collection = connection.get_database('MYPAFWAY')[key]
            counter = 0
            counter_slug_value = ''
            while True:
                counter_slug_value = slug_value
                counter_slug_value += "" if counter == 0 else "-" + str(counter)
                if key == "model":
                    if len(list(collection.find({"children.slug": counter_slug_value}))) == 0:
                        return counter_slug_value
                else:
                    if len(list(collection.find({"slug": counter_slug_value}))) == 0:
                        return counter_slug_value
                counter += 1

        return None
        
class Setting(Document):
    _id = ObjectIdField()
    address = StringField(required=True)
    company_name = StringField(required=True)
    email = StringField(required=True)
    facebook = StringField(default=False)
    instagram = StringField(required=True)
    likedin = StringField(required=True)
    phone = StringField(required=True)
    pinterest = StringField(required=True)
    twitter = StringField(required=True)
    youtube =StringField(required=True)

    meta = {"collection": "mw_settings"}

    def get_json(self):
        return {
            "_id":str(self._id),
            "address": self.address,
            "company_name":self.company_name,
            "email": self.email,
            "facebook":self.facebook,
            "instagram":self.instagram,
            "likedin": self.likedin,
            "phone":self.phone,
            "pinterest":self.pinterest,
            "twitter":self.twitter,
            "youtube":self.youtube
            }



    @classmethod
    def retrieve_all_settings(cls):
        with connect_to_db():

            return [item.get_json() for item in cls.objects()]

    @classmethod
    def find_by_id(cls, id):
        print(id)
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def update_in_db(cls, id, data):
        setting = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                setting[key] = data[key]
            return setting.save()


####################add-attribute-to-category############################################
class Add_attribute_to_category(Document):
    _id = ObjectIdField()
    category_id = StringField(required=True, max_length=256)
    attribute_id=StringField (required=True) 
    status = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = StringField(default=False)
    meta = {'collection': 'mw_add_attribute_to_category'}

    def save_to_db(self):
        with connect_to_db():
            self.save()

    def get_json(self):
        return {
            "_id": str(self._id),
            "category_id": self.category_id,
            "attribute_id": self.attribute_id,          
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def update_in_db_status(cls, id, status):
        attribute_to_category = cls.find_by_id(id)
        with connect_to_db():
            attribute_to_category.status=status
            return attribute_to_category.save()

    @classmethod
    def retrieve_all_attribute_add_to_cat(cls, limit=None, skip=None, status='D',category_id=None):
        all_attributes_add_to_cat = list()
        filter = Q(status__ne='D')
        if category_id:
            filter = filter & Q(category_id=category_id)
        with connect_to_db():
            for item in cls.objects.filter(filter).skip(skip).limit(limit):
                all_attributes_add_to_cat.append(item.get_json())
                
             
                
            return all_attributes_add_to_cat
        