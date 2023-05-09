from flask import Blueprint, request
from flask.views import MethodView

from datetime import datetime

from flask_cors import cross_origin

from app.nr_models import Banner

from helpers import save_image

BannerView = Blueprint('banner_view', __name__)


class fn_Banner_Add_View(MethodView):
    @cross_origin()
    def post(self):
        
        data = request.form
        folder = f"banner/"
        image_path = save_image(request.files['link'], folder)
        print(image_path)
        banner = Banner(
            title=data["title"],
            description=data["description"],
            link=image_path,
            status='A',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        banner.save_to_db()
        return {
            "msg":"updated",
            "status":True,
            "data":{
                
                "title":data["title"],
                "description":data["description"],
                "link":image_path,
                "status":"A",
            }
        }, 200
        



class fn_Banner_Edit_View(MethodView):
    @cross_origin()
    def put(self,id):
        data = dict(request.form)
        folder = f"banner/"
        if request.files['image']:
            image_path = save_image(request.files['image'], folder)
        data['link']=image_path
        banner = Banner.update_in_db(id, data)
        
        return {
            "msg":"id",
            "data":banner.get_json()
        }


class fn_Banner_Find_By_Id(MethodView):
    @cross_origin()
    def get(self, id):
        banner = Banner.find_by_id(id)
        return {
            "msg":"Banner Details",
            "data":banner.get_json()
        }

class fn_Banner_List_View(MethodView):
    @cross_origin()
    def get(self):
        
        return {
            "msg":"List of all banners",
            "data":Banner.retrieve_all_banners()
        }



# # # Creating View Function/Resources
fn_Banner_Add_View= fn_Banner_Add_View.as_view('fn_Banner_Add_View')
fn_Banner_Edit_View = fn_Banner_Edit_View.as_view('fn_Banner_Edit_View')
fn_Banner_List_View = fn_Banner_List_View.as_view('fn_Banner_List_View')
fn_Banner_Find_By_Id = fn_Banner_Find_By_Id.as_view('fn_Banner_Find_By_Id')

# # # adding routes to the Views we just created
BannerView.add_url_rule('/banner_add', view_func=fn_Banner_Add_View, methods=['POST'])
BannerView.add_url_rule('/banner_all', view_func=fn_Banner_List_View, methods=['GET'])
BannerView.add_url_rule('/banner_edit/<string:id>', view_func=fn_Banner_Edit_View, methods=['PUT'])
BannerView.add_url_rule('/banner/<string:id>', view_func=fn_Banner_Find_By_Id, methods=['GET'])


