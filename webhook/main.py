import json
import model
import requests
import dialogflowClient
from chatBotConfig import channel_secret, channel_access_token
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, TextSendMessage, MessageEvent, TextMessage
from umsConfig import umsWebApi

from spotConfig import spotApi, orderApi, userApi
import myModel

# web server for debug
from flask import Flask, request


handler = WebhookHandler(channel_secret)
linebotApi = LineBotApi(channel_access_token)
dialogflowModel = model.DialogflowModel()
userModel = model.UserModel()

# web server for debug
app = Flask(__name__)

@app.route("/")
def index():
    return "this is index"


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
        # spotId
        url = spotApi + "retrieve"
        result = requests.post(url,json=request_input.__dict__)

    print(result.text)
    return result



def replyMessageToUser(replyToken, texts):
    replyMessages = []
    for text in texts:
        replyMessages.append(TextSendMessage(text=text))
    linebotApi.reply_message(replyToken, replyMessages)


# (2) Webhook
@app.route("/webhook",methods=['GET', 'POST'])
# def lineWebhook(request):
def lineWebhook():
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

            pass



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


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0")