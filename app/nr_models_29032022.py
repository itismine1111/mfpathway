from datetime import datetime
from mongoengine import (
    StringField, 
    Document, 
    DateTimeField, 
    EmailField, 
    BooleanField, 
    ObjectIdField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField
)
from mongoengine.queryset.visitor import Q

from mongoengine.errors import DoesNotExist

from helpers import connect_to_db

from bson.objectid import ObjectId

class Banner(Document):
    _id = ObjectIdField()
    title = StringField(required=True, max_length=128)
    description = StringField(required=True)
    image = StringField(required=True, max_length=255)
    link = StringField(required=True, max_length=255)
    status = StringField(required=True, max_length=1)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection':'mw_banners'}
    
    def save_to_db(self): 
        with connect_to_db():   
            self.save()

    def get_json(self):
        return {
            "_id":str(self._id),
            "title":self.title,
            "description":self.description,
            "link":self.link,
            "image":self.image,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }


    @classmethod
    def retrieve_all_banners(cls, limit,skip):
        with connect_to_db():
            return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        banner = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key !="slug":
                    banner[key]=data[key]
            return banner.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

class User(Document):
    
    username = StringField(required=True, max_length=128)
    first_name = StringField(required=True, max_length=255)
    last_name = StringField(required=True, max_length=255)
    email = EmailField(required=True)
    password = StringField()
    email_verified = BooleanField()
    status = StringField(required =True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    

    meta = {'collection':'mw_users'}
    
    def save_to_db(self): 
        with connect_to_db():   
            self.save()

    def get_json(self):
        return {
        'username':self.username, 
        'first_name':self.first_name,
        'last_name':self.last_name, 
        'email':self.email,
        'email_verified':self.email_verified, 
        'status':self.status,
        'created_at':self.created_at, 
        'updated_at':self.updated_at
        }


    @classmethod
    def retrieve_all_banners(cls):
        with connect_to_db():
            return [item.get_json() for item in cls.objects(status='A')]

    @classmethod
    def update_in_db(cls, id, data):
        banner = cls.find_by_id(id)
        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at":
                    banner[key]=data[key]
            return banner.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(id=id)

    @classmethod
    def find_by_email(cls, email):
        with connect_to_db():
            try:
                return cls.objects.get(email=email)
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

    meta = {'collection':'mw_services'}
    
    def save_to_db(self): 
        with connect_to_db():   
            self.save()

    def get_json(self):
        return {
            "_id":str(self._id),
            "name":self.name,
            "image":self.image,
            "description":self.description,
            "slug":self.slug,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }


    @classmethod
    def retrieve_all_services(cls, limit,skip):
        with connect_to_db():
            return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]


    @classmethod
    def update_in_db(cls, id, data):
        services = cls.find_by_id(id)



        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key !='link' or key!="slug":
                    services[key]=data[key]
                services['updated_at'] = datetime.now()
            return services.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))
        
class Faq(Document):
    _id = ObjectIdField()
    question = StringField(required=True, max_length=128)
    answer = StringField(required=True, max_length=255)
    status = StringField(required=True, max_length=1)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection':'mw_faq'}
    
    def save_to_db(self): 
        with connect_to_db():   
            self.save()

    def get_json(self):
        return {
            "_id":str(self._id),
            "question":self.question,
            "answer":self.answer,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }


    @classmethod
    def retrieve_all_faq(cls, limit,skip):
        with connect_to_db():
            return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        faq = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at":
                    faq[key]=data[key]
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

    meta = {'collection':'mw_blogs'}
    
    def save_to_db(self): 
        with connect_to_db():   
            self.save()

    def get_json(self):
        return {
            "_id":str(self._id),
            "name":self.name,
            "link":self.link,
            "image":self.image,
            "slug":self.slug,
            "description":self.description,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }


    @classmethod
    def retrieve_all_blogs(cls, limit,skip):
        with connect_to_db():
            return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]


    @classmethod
    def update_in_db(cls, id, data):
        blogs = cls.find_by_id(id)


        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key !="slug":
                    blogs[key]=data[key]
                blogs['updated_at'] = datetime.now()
            return blogs.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

class SubCategory(EmbeddedDocument):
    _id = ObjectIdField()
    title=StringField(required=True, max_length=100)
    image=StringField(required=True)
    description=StringField(required=True)
    status = StringField(required=True, max_length=10)
    slug = StringField(required=True, max_length=128)
    parent = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    def get_json(self):
        return{
            "_id":str(self._id),
            "title":self.title,
            "image":self.image,
            "description":self.description,
            "status":self.status,
            "slug":self.slug,
            "created_at":self.created_at,
            "updated_at":self.updated_at,
            "parent":self.parent
        }
    
    @staticmethod
    def update_in_db(category_id,id,data):
        category = Category.find_by_id(category_id)
        for subcategory in category.children:
            if str(subcategory._id) == id:
                for key in data.keys():
                    if key != "created_at" and key != "updated_at" and key!="slug" and key!="parent_id":
                        
                        subcategory[key]=data[key]
                    subcategory['updated_at'] = datetime.now()
        return category.save_to_db()

    @staticmethod
    def find_by_id(category_id,id):
        category = Category.find_by_id(category_id)
        for subcategory in category.children:
            if str(subcategory._id) == id:
                return subcategory
        return None

class Category(Document):
    _id=ObjectIdField()
    title=StringField(required=True, max_length=100)
    image=StringField(required=True)
    slug = StringField(required=True, max_length=128, unique=True)
    description=StringField(required=True)
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    children = ListField(EmbeddedDocumentField(SubCategory))

    meta={"collection":"mw_parent"}

    def save_to_db(self):
        with connect_to_db():
            self.save()
    
    def get_json(self, children=False):
        
        return{
            "_id":str(self._id),
            "title":self.title,
            "image":self.image,
            "description":self.description,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at,
            "slug":self.slug,
            "children":self.retrieve_all_subcategories() if children else None
        }

    @classmethod
    def retrieve_all_categories(cls, limit=None,skip=None, children=False):
        with connect_to_db():
            return [item.get_json(children) for item in cls.objects.filter(status__ne='D').skip(skip).limit(limit)]

    def retrieve_all_subcategories(self, limit=None,skip=None):
        with connect_to_db():
            subcategory_list = []
            if skip is None:
                skip = 0
            if limit is None:
                limit=len(self.children)
            for item in self.children[skip:skip+limit]:
                if item.status != 'D':
                    subcategory_list.append(item.get_json())
            return subcategory_list
    
    @classmethod
    def update_in_db(cls, id, data):
        print(id)
        category = cls.find_by_id(id)


        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at" or key!="slug":
                    category[key]=data[key]
                category['updated_at'] = datetime.now()
            return category.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))


def find_value_by_slug(key, slug_value):
    with connect_to_db() as connection:
        key_list = ["mw_services","mw_blogs","mw_parent","subcategory"]
        if key in key_list :
            if key == "subcategory":
                collection =  connection.get_database('MYPAFWAY')["mw_parent"]
                return collection.find_one({"children.slug":slug_value})
            else:
                collection =  connection.get_database('MYPAFWAY')[key]
                return collection.find_one({"slug":slug_value})        
        return None

def insert_number_in_slug(key, slug_value):
    with connect_to_db() as connection:
        key_list = ["mw_services","mw_blogs","mw_parent","subcategory"]
        if key in key_list:
            if key == "subcategory":
                collection = connection.get_database('MYPAFWAY')["mw_parent"]
            else:
                collection = connection.get_database('MYPAFWAY')[key]
            counter=0
            counter_slug_value=''
            while True:
                counter_slug_value = slug_value
                counter_slug_value += "" if counter == 0 else "-" + str(counter)
                if key == "subcategory":
                    if (len(list(collection.find({"children.slug":counter_slug_value}))) == 0):                  
                        return counter_slug_value
                else:
                    if (len(list(collection.find({"slug":counter_slug_value}))) == 0):                  
                        return counter_slug_value
                counter +=1

        return None

        
