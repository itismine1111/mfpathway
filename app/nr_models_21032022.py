from mongoengine import StringField, Document, DateTimeField, EmailField, BooleanField

from mongoengine.errors import DoesNotExist

from helpers import connect_to_db

class Banner(Document):

    title = StringField(required=True, max_length=128)
    description = StringField(required=True, max_length=255)
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
            "title":self.title,
            "description":self.description,
            "link":self.link,
            "image":self.image,
            "status":self.status,
            "created_at":self.created_at,
            "updated_at":self.updated_at
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
                banner[key]=data[key]
            return banner.save()

    @classmethod
    def find_by_id(cls, id):
        with connect_to_db():
            return cls.objects.get(id=id)

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

    