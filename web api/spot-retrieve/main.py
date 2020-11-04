import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from model import SpotModel,ResponseModel,QueryModel

# data model
spot = SpotModel()
response = ResponseModel()

# firebase
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)
db = firestore.client()

# firebase data collection
spots_ref = db.collection("spots")

def retrieve(request):
    # 获取参数
    # https://cloud.google.com/functions/docs/quickstart-python

    request_json = request.get_json()
    request_args = request.args

    # id
    if request_json and "id" in request_json:
        id = request_json["id"]
    elif request_args and "id" in request_args:
        id = request_args["id"]
    else:
        id = None

    # name
    if request_json and "name" in request_json:
        name = request_json["name"]
    elif request_args and "name" in request_args:
        name = request_args["name"]
    else:
        name = None

    # address
    if request_json and "address" in request_json:
        address = request_json["address"]
    elif request_args and "address" in request_args:
        address = request_args["address"]
    else:
        address = None

    # 测试用参数
    # id = "1000"
    # name = None
    # address = None

    # debug
    print(request_json)
    print("%s,%s,%s" % (type(id),type(name),type(address)))
    print("%s,%s,%s" % (str(id),str(name),str(address)))

    if((id != "") and (not id is None)):
        # 根据id精确查找
        spot = spots_ref.document(id).get().to_dict()
        result = []
        
        if(spot != None):
            # 返回结果
            result.append(spot)
            response.status = "1"
            response.result = result
        else:
            # 返回未找到
            response.status = "0"
            response.result = "未找到相關資料"
        
    elif((name != "") and (not name is None)):
        # 根据名称查找

        # 取出所有
        spots = [spot.to_dict() for spot in spots_ref.stream()]
        result = []

        # 模糊查找关键字 name
        for item in spots:
            if(name in item.get("name")):
                result.append(item)

        # 返回结果条数和结果
        response.status = len(result)
        response.result = result
    
    elif((address != "") and (not address is None)):
        # 根据地址查找
        # 取出所有
        spots = [spot.to_dict() for spot in spots_ref.stream()]
        result = []

        # 模糊查找关键字 name
        for item in spots:
            # 分别取出乡镇和详细地址
            # 防止查询为空的处理
            spotsCityAndTown = str(item.get("city")) + str(item.get("town"))
            spotsAddress = str(item.get("address"))

            if((address in spotsCityAndTown) or (address in spotsAddress)):
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

# 测试request
# retrieve("test")