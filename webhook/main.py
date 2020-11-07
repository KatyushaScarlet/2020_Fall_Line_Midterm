import json
import model
import requests
import dialogflowClient
from chatBotConfig import channel_secret, channel_access_token
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, TextSendMessage, MessageEvent, TextMessage
from umsConfig import umsWebApi

from myConfig import spotApi, orderApi, userApi
import myModel

# web server for debug
from flask import Flask, request


handler = WebhookHandler(channel_secret)
linebotApi = LineBotApi(channel_access_token)
dialogflowModel = model.DialogflowModel()
userModel = model.UserModel()

# web server for debug
# app = Flask(__name__)

# @app.route("/")
# def index():
#     return "this is index"


# (1) functions
def model_init_(lineId):
    global dialogflowModel, userModel
    dialogflowModel = model.DialogflowModel()
    userModel = model.UserModel()
    dialogflowModel.lineId = userModel.lineId = lineId


def actionDispatch():
    url = umsWebApi + dialogflowModel.actionName
    
    if (dialogflowModel.actionName in ['create', 'delete', 'update']):
        result = requests.post(url, json=userModel.__dict__)
        
    elif (dialogflowModel.actionName == 'retrieve'):
        result = requests.get(url + '?phone=' + userModel.phone)

    return result

# custom function call web api
def callWebApi(actionName,request_input):
    # 根据action不同，传入参数不同，调用不同的web api
    if ("querySpotVia" in actionName):
        # query spot
        url = spotApi + "retrieve"

    elif(actionName == "checkUser"):
        # check user
        url = userApi + "check"

    elif(actionName == "bookTicket"):
        # book ticket
        url = orderApi + "create"

    elif(actionName == "checkOrder"):
        # check order
        url = orderApi + "retrieve"

    else:
        Exception()

    json_request = request_input.__dict__
    result = requests.post(url,json=json_request) 

    return result



def replyMessageToUser(replyToken, texts):
    replyMessages = []
    for text in texts:
        replyMessages.append(TextSendMessage(text=text))
    linebotApi.reply_message(replyToken, replyMessages)


# (2) Webhook
# for flask
# @app.route("/webhook",methods=['GET', 'POST'])
# def lineWebhook():
def lineWebhook(request):

    # get X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature')

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return '200 OK'


# (3) Follow Event
@handler.add(FollowEvent)
def handle_follow(event):
    model_init_(event.source.user_id)
    dialogflowModel.lineId = event.source.user_id
    dialogflowModel.eventName = 'welcomeEvent'
    dialogflowClient.eventDispatch(dialogflowModel)
    replyMessageToUser(event.reply_token, dialogflowModel.responses)


# (4) Message Event
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    model_init_(event.source.user_id)
    dialogflowModel.queryInput = event.message.text
    dialogflowClient.queryDispatch(dialogflowModel)
    
    if (dialogflowModel.actionName):
        
        # hack custom code
        # 调用callWebApi呼叫自定义api
        # 用event.reply_token和dialogflowModel.responses直接调用replyMessageToUser

        actionName = dialogflowModel.actionName
        response = myModel.ResponseModel()
        response_text = ""
        texts = []
        if ("querySpotVia" in dialogflowModel.actionName):
            #查询类
            spotRetrieveModel = myModel.SpotRetrieveModel() 

            if (actionName == "querySpotViaId"):
                # 通过id查询
                spotRetrieveModel.id = dialogflowModel.parameters["spotId"]

            elif (actionName == "querySpotViaName"):
                # 通过名称查询
                spotRetrieveModel.name = dialogflowModel.parameters["spotName"] 

            elif (actionName == "querySpotViaAddress"):
                # 通过地址查询
                spotRetrieveModel.address = dialogflowModel.parameters["spotAddress"]

            else:
                print("No method handle:" + actionName)
                pass

            # call web api
            result = callWebApi(actionName,spotRetrieveModel)
            response.__dict__ = json.loads(result.text)
            count = int(response.status)
            
            if(count > 1):
                # 查询到多条结果，显示前N个，
                limit = 10 if count > 10 else count
                spots = response.result[:limit]
                response_text += "查詢到 {n} 條結果，顯示前 {l} 條：\n".format(n=str(count),l=str(limit))
                for item in spots:
                    spot = myModel.SpotModel()
                    spot.__dict__ = item
                    response_text += "{id}. {name}\n".format(id=spot.id,name=spot.name)
                pass


            elif(count == 1):
                # 查询到一条结果，显示详细信息
                spot = myModel.SpotModel()
                spot.__dict__ = response.result[0]

                # 优先取address，若为空则取city+town
                address = spot.address if spot.address != "" else spot.city + spot.town

                response_text += "查詢結果：\n"
                response_text += "\n"   
                response_text += "景點序號：{}\n".format(spot.id)
                response_text += "景點名稱：{}\n".format(spot.name)
                response_text += "景點簡介：{}\n".format(spot.description)
                response_text += "景點地址：{}\n".format(address)
                response_text += "開放時間：{}\n".format(spot.time)
                response_text += "聯係方式：{}\n".format(spot.phone)
                response_text += "購票信息：{}\n".format(spot.ticket)
                response_text += "重要提醒：{}\n".format(spot.remark)
                pass

            elif(count == 0):
                # 查询不到
                response_text += "很抱歉，沒有找到相關資訊"
                pass

            else:
                # 查询出错
                response_text += "錯誤：\n"
                response_text += str(response.result)
                pass
            
            texts.append(response_text)
            replyMessageToUser(event.reply_token,texts)
            return

        elif (dialogflowModel.actionName == "bookTicket" or dialogflowModel.actionName == "checkOrder"):
            # 订票
            # 查询用户是否注册
            actionName = "checkUser"
            userCheck = myModel.UserCheckModel()
            userCheck.lineId = dialogflowModel.lineId
            result = callWebApi(actionName,userCheck)

            response.__dict__ = json.loads(result.text)
            count = int(response.status)

            if(count == 1):
                # 用户已注册
                user = myModel.UserModel()
                user.__dict__ = response.result
                
                if(dialogflowModel.actionName == "bookTicket"):
                    # 订票流程
                    actionName = "bookTicket"
                    # 创建订票请求
                    orderCreateModel = myModel.OrderCreateModel()
                    orderCreateModel.userid = user.phone
                    orderCreateModel.spotid = dialogflowModel.parameters["spotId"]
                    orderCreateModel.count = dialogflowModel.parameters["count"]
                    # 订票
                    result = callWebApi(actionName,orderCreateModel)
                    response.__dict__ = json.loads(result.text)
                    status = int(response.status)

                    if(status == 1):
                        # 訂票成功
                        response_text += "訂票成功！"
                    else:
                        # 訂票失敗
                        response_text += "訂票失敗：\n"
                        response_text += str(response.result)

                elif(dialogflowModel.actionName == "checkOrder"):
                    # 查询订单流程
                    actionName = "checkOrder"
                    # 创建查询请求
                    orderRetrieveModel = myModel.OrderRetrieveModel()
                    orderRetrieveModel.userid = user.phone
                    # 查询
                    result = callWebApi(actionName,orderRetrieveModel)
                    response.__dict__ = json.loads(result.text)
                    count = int(response.status)

                    if (count > 0):
                        orders = response.result

                        response_text += "找到 {} 條記錄：\n".format(count)
                        for item in orders:
                            order = myModel.OrderModel()
                            order.__dict__ = item
                            response_text += "[{}]{} - {}張票\n".format(order.datetime,order.spot.get("name"),round(order.count))
                    elif (count == 0):
                        response_text += "未找到訂單記錄"
                    else:
                        response_text += "错误：\n"
                        response_text += response.result
                else:
                    pass

            else:
                # 用户未注册
                response_text += "請先注冊"

            texts.append(response_text)
            replyMessageToUser(event.reply_token,texts)
            return

        # elif (actionName == "checkOrder"):
        #     # 查看订单
        #     orderRetrieveModel = myModel.OrderRetrieveModel()
        #     orderRetrieveModel.userid = 
        #     pass
        else:
            # 原代码
            if (dialogflowModel.actionName == 'update'):
                dialogflowModel.actionName = 'retrieve'
                userModel.phone = dialogflowModel.parameters['phone']
                result = actionDispatch()
                originalUserData = json.loads(result.text)['userModel']
                newUserData = json.loads(result.text)['userModel']
                
                for key in dialogflowModel.parameters:
                    newUserData[key] = dialogflowModel.parameters[key]
                    
                dialogflowModel.parameters = newUserData
                dialogflowModel.actionName = 'update'
            
            for key in dialogflowModel.parameters:
                setattr(userModel, key, dialogflowModel.parameters[key])
                
            result = actionDispatch()
            
            if (json.loads(result.text)['result']['code'] == '1'):
                dialogflowModel.parameters = json.loads(result.text)['userModel']
                dialogflowModel.eventName = dialogflowModel.actionName + '_responseEvent'  
                
            else:
                dialogflowModel.eventName = dialogflowModel.actionName + '_failResponseEvent'
                
            if (dialogflowModel.actionName == 'update'):
                dialogflowModel.parameters = originalUserData

            dialogflowClient.eventDispatch(dialogflowModel)

    replyMessageToUser(event.reply_token, dialogflowModel.responses)


# if __name__ == "__main__":
#     app.run(debug = True, host = "0.0.0.0")