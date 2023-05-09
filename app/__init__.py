from flasgger import Swagger
from flask import Flask, redirect
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from Settings.config import app_config

from app.banner.views import BannerView

bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)
    # app.config.from_object(app_config[config_name])
    app.config.from_object(app_config['development'])
    app.config['SWAGGER'] = {
        'swagger': '2.0',
        'title': 'ASERFI',
        'description': "☆ ☯  𝕿𝖍𝖎𝖘 𝖎𝖘 𝖆 𝕽𝕰𝕾𝕿𝖋𝖚𝖑 Ａℙ𝐢 𝖇𝖚𝖎𝖑𝖙 𝖎𝖓 𝖕𝖞𝖙𝖍𝖔𝖓 𝖚𝖘𝖎𝖓𝖌 𝖙𝖍𝖊 "
                       "𝕱𝖑𝖆𝖘𝖐 𝕱𝖗𝖆𝖒𝖊𝖜𝖔𝖗𝖐  ♤ ◉‿◉.\ \n︻デ═一   ---      ---       ---         ---            "
                       "---              ---                ---               ---\n𝕬𝖚𝖙𝖍𝖔𝖗 : 𝔰𝔥𝔞𝔨𝔶𝔞 "
                       "𝔡𝔲𝔱𝔱𝔞(◣_◢) \n ︻デ═一   ---      ---       ---         ---            ---              ---  "
                       "              ---               --- "
                       "\n 𝕮𝖔𝖒𝖕𝖆𝖓𝖞  : ɪᴠᴀɴ ɪɴꜰᴏᴛᴇᴄʜ\n︻デ═一   ---      ---       ---         ---            ---  "
                       "            ---                ---               --",
        'contact': {
            'Developer': 'Shakya Dutta',
            'Company': 'IVAN Infotech',
        },

        'schemes': [
            'http'
        ],

        'license': {
            'name': 'private'
        },

        'specs_route': '/apidocs/'
    }
    bcrypt.init_app(app)
    CORS(app)
    swagger = Swagger(app)

    @app.route('/')
    def index():
        return redirect('/apidocs/')

    from app.admin.views import admin_auth

    app.register_blueprint(admin_auth)
    app.register_blueprint(BannerView)

    return app
