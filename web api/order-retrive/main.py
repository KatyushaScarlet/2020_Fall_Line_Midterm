import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from model import OrderModel,ResponseModel

# data model
order = OrderModel()
response = ResponseModel()

# firebase
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)
db = firestore.client()

# firebase data collection
orders_ref = db.collection("orders")

def retrieve(request):
    # # debug
    # orderid = ""
    # userid = ""
    # spotid = "5374"

    # 获取参数
    request_json = request.get_json()
    request_args = request.args

    # orderid
    if request_json and "orderid" in request_json:
        orderid = request_json["orderid"]
    elif request_args and "orderid" in request_args:
        orderid = request_args["orderid"]
    else:
        orderid = ""

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

    if(orderid != ""):
        # 根据订单id查找
        order = orders_ref.document(orderid).get().to_dict()

        if(order != None):
            # 返回结果
            response.status = "1"
            response.result = order
        else:
            # 返回未找到
            response.status = "0"
            response.result = "未找到相關資料"

    elif(userid != ""):
        # 根据用户id查找

        # 取出所有
        orders = [order.to_dict() for order in orders_ref.stream()]
        result = []

        # 根据用户id查找
        for item in orders:
            if(userid == item.get("user").get("phone")):
                result.append(item)

        # 返回结果条数和结果
        response.status = len(result)
        response.result = result

    elif(spotid != ""):
        # 根据景点id查找:

        # 取出所有
        orders = [order.to_dict() for order in orders_ref.stream()]
        result = []

        # 根据景点id查找
        for item in orders:
            if(spotid == item.get("spot").get("id")):
                result.append(item)

        # 返回结果条数和结果
        response.status = len(result)
        response.result = result

    else:
        # 返回错误
        response.status = "-1"
        response.result = "请输入查找条件"

    # 返回结果
    print("response: " + str(response.status))
    return response.__dict__

# # 测试request
# retrieve("test")