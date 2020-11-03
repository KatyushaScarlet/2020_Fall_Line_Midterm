import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from model import UserModel,SpotModel,OrderModel,ResponseModel
import time
import uuid

# data model
user = UserModel()
spot = SpotModel()
order = OrderModel()
response = ResponseModel()

# firebase
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)
db = firestore.client()

# firebase data collection
users_ref = db.collection("users")
spots_ref = db.collection("spots")
orders_ref = db.collection("orders")

def create(request):
    # 获取参数
    request_json = request.get_json()
    request_args = request.args

    # orderid
    orderid = str(uuid.uuid1())
    order.id = orderid

    # userid
    if request_json and "userid" in request_json:
        userid = request_json["userid"]
    elif request_args and "userid" in request_args:
        userid = request_args["userid"]
    else:
        userid = ""

    # spotid
    if request_json and "spotid" in request_json:
        spotid = request_json["spotid"]
    elif request_args and "spotid" in request_args:
        spotid = request_args["spotid"]
    else:
        spotid = ""
    # count
    if request_json and "count" in request_json:
        count = request_json["count"]
    elif request_args and "count" in request_args:
        count = request_args["count"]
    else:
        count = ""

    # debug
    # userid = "0123456789"
    # spotid = "1"
    # order.count = "2"

    order.datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    pass

    # 根据userid查找user
    if(userid != ""):
        user = users_ref.document(userid).get().to_dict()

        if(user != None):
            # 获取user
            order.user = user
        else:
            # 返回未找到
            response.status = "0"
            response.result = "未找到該用戶相關資料"
            return response.__dict__
    else:
        # 返回条件缺失
        response.status = "-1"
        response.result = "請輸入用戶"
        return response.__dict__

    # 根据spotid查找spot
    if(spotid != ""):
        spot = spots_ref.document(spotid).get().to_dict()

        if(spot != None):
            # 获取spot
            order.spot = spot
        else:
            # 返回未找到
            response.status = "0"
            response.result = "未找到該景點相關資料"
            return response.__dict__
    else:
        # 返回条件缺失
        response.status = "-1"
        response.result = "請輸入景點"
        return response.__dict__

    # count 为空则默认为1
    order.count = count if count != "" else "1"

    # 新增订单
    orders_ref.document(orderid).set(order.__dict__)
    response.status = "1"
    response.result = "創建訂單成功"
    print(response)
    return response.__dict__

# debug
# result = create("test")
# print(result)