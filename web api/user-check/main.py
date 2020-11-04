import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from model import UserModel, ResponseModel

# data model
user = UserModel()
response = ResponseModel()

# firebase
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)
db = firestore.client()

# firebase data collection
users_ref = db.collection("users")

def check(request):
    # 获取参数
    request_json = request.get_json()
    request_args = request.args

    # lineId
    if request_json and "lineId" in request_json:
        lineId = request_json["lineId"]
    elif request_args and "lineId" in request_args:
        lineId = request_args["lineId"]
    else:
        lineId = None

    # 测试用参数
    # lineId = "Uedef6a810f69246dc30b3c15afdcb2f4"

    if((lineId != "") and (not lineId is None)):
        # 根据lineid查找
        # 取出所有
        users = [item.to_dict() for item in users_ref.stream()]
        result = []

        # 查找lineid相同的
        for item in users:
            if(str(item.get("lineId")) == lineId):
                result.append(item)

        if(len(result)!=0):
            response.status = "1"
            response.result = result[0]
        else:
            response.status = "0"
            response.result = "未找到用戶資料"
    
    else:
        # 返回错误
        response.status = "-1"
        response.result = "參數缺失"

    # 返回结果
    print("response: " + str(response.status))
    return response.__dict__

# 测试request
# check("test")
