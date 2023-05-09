from enum import unique
from mongoengine import StringField, Document, DateTimeField, EmailField, BooleanField, ObjectIdField

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
                if key != "created_at" or key != "updated_at":
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
                if key != "created_at" or key != "updated_at" or key !='link':
                    services[key]=data[key]
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
                if key != "created_at" or key != "updated_at":
                    blogs[key]=data[key]
            return blogs.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

class Category(Document):
    _id=ObjectIdField()
    title=StringField(required=True, max_length=100)
    image=StringField(required=True)
    slug = StringField(required=True, max_length=128, unique=True)
    description=StringField(required=True)
    parent=StringField(required=True)
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta={"collection":"mw_category"}

    def save_to_db(self):
        with connect_to_db():
            self.save()
    
    def get_json(self):
        return{
            "_id":str(self._id),
            "title":self.title,
            "image":self.image,
            "slug":self.slug,
            "description":self.description,
            "parent":self.parent,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at

        }
    @classmethod
    def retrieve_all_categories(cls, limit,skip):
        with connect_to_db():
            return [item.get_json() for item in cls.objects(status__ne='D').skip(skip).limit(limit)]

    @classmethod
    def update_in_db(cls, id, data):
        category = cls.find_by_id(id)


        with connect_to_db():
            for key in data.keys():
                if key != "created_at" or key != "updated_at":
                    category[key]=data[key]
            return category.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

def find_value_by_slug(key, slug_value):
    with connect_to_db() as connection:
        collection =  connection.get_database('MYPAFWAY')[key]
        if key == "mw_services" or key == "mw_blogs" or key == "mw_category":
            return collection.find_one({"slug":slug_value})
        
        return None

def insert_number_in_slug(key, slug_value):
    with connect_to_db() as connection:
        if key not in connection.get_database('MYPAFWAY').list_collection_names():
            return None

        collection = connection.get_database('MYPAFWAY')[key]
        if key =="mw_blogs" or key == "mw_services" or key == "mw_category": 
            counter=0
            counter_slug_value=''
            while True:
                counter_slug_value = slug_value
                counter_slug_value += "" if counter == 0 else "-" + str(counter)
                if (len(list(collection.find({"slug":counter_slug_value}))) == 0):
                    
                    return counter_slug_value
                counter +=1

        return None

        
