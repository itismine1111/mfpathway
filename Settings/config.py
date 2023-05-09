import os


class Config:
    USER_SECRET_KEY = 'its nolonger a secret'
    ADMIN_SECRET_KEY = 'secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = ''


class DevelopmentConfig(Config):
# class ProductionConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'secret'
    USER_SECRET_KEY = 'qwerty@123456798'
    ADMIN_SECRET_KEY = 'secret'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site2.db'
    # mysql://root:Ivan@123@localhost/app_db
    # SQLALCHEMY_DATABASE_URI = 'postgresql://dev13ivantechnol_usr1_grse:2iEvwLNmmXxA@localhost/dev13ivantechnol_db1_grse'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost/dev13ivantechnol_usr1_grse_2'
    #MONGODB_SETTINGS = {'db': 'MYPAFWAY','host': 'localhost','port': 1157,''}


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USER_SECRET_KEY = 'i wont tell if you dont'
    ADMIN_SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = ''


class StagingConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    USER_SECRET_KEY = 'its nolonger a secret'
    ADMIN_SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
# class DevelopmentConfig(Config):
    DEBUG = False
    TESTING = False
    USER_SECRET_KEY = 'its nolonger a secret'
    ADMIN_SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
