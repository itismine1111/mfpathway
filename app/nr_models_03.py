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
    ListField,
    FloatField,
    ReferenceField
)
from mongoengine.queryset.visitor import Q

from mongoengine.errors import DoesNotExist

from helpers import connect_to_db

from bson.objectid import ObjectId

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

#schema based models

class Category(Document):
    _id = ObjectIdField()
    title=StringField(required=True, max_length=100)
    image=StringField(required=True)
    description=StringField(required=True)
    status = StringField(required=True, max_length=10)
    slug = StringField(required=True, max_length=128)
    parent_id = StringField()
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {"collection":"mw_category"}

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
                if key != "created_at" and key != "updated_at" and key!="slug":
                    category[key]=data[key]
                category['updated_at'] = datetime.now()
            return category.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def retrieve_all_categories(cls, limit=None,skip=None, children=False):
        with connect_to_db():
            data = []
            for item in cls.objects.filter(status__ne='D').skip(skip).limit(limit):
                if item.parent_id is None:
                    data.append(item.get_json(children, True))
            return data

    @classmethod
    def retrieve_all_subcategories(cls,category_id, limit=None,skip=None ):
        with connect_to_db():
            data = []
            for item in cls.objects.filter(Q(status__ne='D') & Q(parent_id__ne=None)).skip(skip).limit(limit):
                if item.parent_id == str(category_id):
                    data.append(item.get_json(False,False))
            return data
    

    def get_json(self, children=False, category=True):
        return{
            "_id":str(self._id),
            "title":self.title,
            "image":self.image,
            "description":self.description,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at,
            "slug":self.slug,
            "parent_id":None if category else self.parent_id,
            "children":self.retrieve_all_subcategories(self._id) if children and category else None
        }


class MakeModel(EmbeddedDocument):
    id=ObjectIdField()

    name=StringField(required=True, max_length=100)
    image=StringField(required=True)
    description=StringField(required=True)
    status = StringField(required=True, max_length=10)
    slug = StringField(required=True, max_length=128)
    parent = StringField(required=True)#Brand
    year=StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    def get_json(self):
        return{
            "id":str(self.id),
            "name":self.name,
            "image":self.image,
            "description":self.description,
            "status":self.status,
            "slug":self.slug,
            "parent":self.parent,
            "year":self.year,
            "created_at":self.created_at,
            "updated_at":self.updated_at,
           
        }
    
class Brand(Document):
    _id=ObjectIdField()
    name=StringField(required=True, max_length=100)
    image=StringField(required=True)
    slug = StringField(required=True, max_length=128, unique=True)
    description=StringField(required=True)
    status = StringField(required=True, max_length=10)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    children = ListField(EmbeddedDocumentField(MakeModel))

    meta={"collection":"mw_brand"}

    def save_to_db(self):
        with connect_to_db():
            self.save()
    
    def get_json(self, children=False):
        
        return{
            "_id":str(self._id),
            "name":self.name,
            "image":self.image,
            "description":self.description,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at,
            "slug":self.slug,
            "children":self.retrieve_all_model() if children else None
        }

    @classmethod
    def retrieve_all_brand(cls, limit=None,skip=None, children=False):
        with connect_to_db():
            return [item.get_json(children) for item in cls.objects.filter(status__ne='D').skip(skip).limit(limit)]

    def retrieve_all_model(self, limit=None,skip=None):
        with connect_to_db():
            model_list = []
            if skip is None:
                skip = 0
            if limit is None:
                limit=len(self.children)
            for item in self.children[skip:skip+limit]:
                if item.status != 'D':
                    model_list.append(item.get_json())
            return model_list
    
    @classmethod
    def update_in_db(cls, id, data):
        brand = cls.find_by_id(id)


        with connect_to_db():
            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key!="slug":
                    brand[key]=data[key]
            return brand.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def find_by_model_id(cls, id):
        with connect_to_db():
            brand = cls.objects.filter(children__id=id).first()
            for make_model in brand.children:
                if make_model.id == ObjectId(id):
                    return make_model        
            return None

    @classmethod
    def update_model(cls,id, data):
         with connect_to_db():
            brand = cls.objects.filter(children__id=id).first()
            for make_model in brand.children:
                if make_model.id == ObjectId(id):
                    print(data.keys())
                    for key in data.keys():
                        
                        if key != "created_at" and key != "updated_at" and key!="slug":
                            make_model[key]=data[key]
                    return brand.save()

class AutopartProduct(Document):
    _id = ObjectIdField()
    name = StringField(required=True, max_length=128)
    short_description = StringField(requried=True)
    description = StringField(required=True)
    regular_price = FloatField(requried=True)
    sale_price = FloatField(required=True)
    status = StringField(requried=True)
    slug = StringField(required=True, max_length=128)
    created_at = DateTimeField(requried=True)
    updated_at = DateTimeField(required=True)

    parent_id = StringField(required=True)

    meta={"collection":"mw_autopart_product"}

    def get_json(self):
        return{
            "_id":str(self._id),
            "title":self.title,
            "image":self.image,
            "description":self.description,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at,
            "slug":self.slug,
            "parent_id": self.parent_id
        }

    def save_to_db(self):
        with connect_to_db():
            self.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(_id=ObjectId(id))

    @classmethod
    def update_in_db(cls, id, data):
        product = cls.find_by_id(id)

        with connect_to_db():
            for key in data.keys():
                if key != "created_at" and key != "updated_at" and key!="slug":
                    product[key]=data[key]
            product['updated_at'] = datetime.now()
            return product.save()

    @classmethod
    def retrieve_all_products(cls, limit=None,skip=None):
        with connect_to_db():
            data = []
            for item in cls.objects.filter(status__ne='D').skip(skip).limit(limit):
                if item.parent_id is None:
                    data.append(item.get_json)
            return data

def find_value_by_slug(collection_name, slug_value):
    with connect_to_db() as connection:
        key_list = ["mw_services","mw_blogs","mw_category","mw_autopart_product","mw_brand","model"]
        if collection_name in key_list :
            
            if collection_name == "model":
                collection =  connection.get_database('MYPAFWAY')["mw_brand"]
                return collection.find_one({"children.slug":slug_value})
            else:
                collection =  connection.get_database('MYPAFWAY')[collection_name]
                return collection.find_one({"slug":slug_value})        
        return None

def insert_number_in_slug(key, slug_value):
    with connect_to_db() as connection:
        key_list = ["mw_services","mw_blogs","mw_category","mw_autopart_product","mw_brand","model"]
        if key in key_list:
            if key == "model":
                collection = connection.get_database('MYPAFWAY')["mw_brand"]
            else:
                collection = connection.get_database('MYPAFWAY')[key]
            counter=0
            counter_slug_value=''
            while True:
                counter_slug_value = slug_value
                counter_slug_value += "" if counter == 0 else "-" + str(counter)
                if key == "model":
                    if (len(list(collection.find({"children.slug":counter_slug_value}))) == 0):                  
                        return counter_slug_value
                else:
                    if (len(list(collection.find({"slug":counter_slug_value}))) == 0):                  
                        return counter_slug_value
                counter +=1

        return None

        
