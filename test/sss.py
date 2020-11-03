from chatBotConfig import channel_secret, channel_access_token
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, TextSendMessage, MessageEvent, TextMessage
import json
import requests

handler = WebhookHandler(channel_secret)
line_bot_api = LineBotApi(channel_access_token)

# (0) Messages
welcomeMessage = TextSendMessage(text='歡迎關注')
menuMessage = TextSendMessage(text='本系統提供下列功能：\n' \
                                    + '1. 註冊\n' \
                                    + '2. 退出\n' \
                                    + '3. 列表\n' \
                                    + '4. 修改\n' \
                                    + '請輸入所需選項......')
createUserMessage = TextSendMessage(text='名稱：回到1920 臺北設市百年：青年的誕生-文協百年特展\n開始時間：2020/10/11 09:30:00\n結束時間：2020/12/31 17:30:00\n地址：臺北市大同區寧夏路89號'\
+'\n\n名稱：2020臺北地景公共藝術計畫：朝霧記\n開始時間：2020/10/16 08:00:00\n結束時間：2020/11/15 22:00:00\n地址：臺北市全區域')
deleteUserMessage = TextSendMessage(text='收到，我將為您辦理退出手續')
userListMessage = TextSendMessage(text='收到，我將為您呈現人員列表')
updateUserMessage = TextSendMessage(text='收到，我將為您辦理資料修改手續')
errorMessage = TextSendMessage(text='哦，這超出我的能力範圍......')


# (1) Webhook
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


# (2) Follow Event
@handler.add(FollowEvent)
def handle_follow(event):
    replyMessages = [welcomeMessage, menuMessage]
    line_bot_api.reply_message(event.reply_token, replyMessages)


# (3) Message Event
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    command = event.message.text
    
    if (command in ['1', '台北', '臺北']):
        replyMessages = getText(command)
        
    elif (command in ['2', '退出', '退選']):
        replyMessages = deleteUserMessage
        
    elif (command in ['3', '列表', '清單']):
        replyMessages = userListMessage
        
    elif (command in ['4', '修改', '變更']):
        replyMessages = updateUserMessage
    
    else:
        replyMessages = [errorMessage, menuMessage]
                                                                                    
    line_bot_api.reply_message(event.reply_token, replyMessages)

def getText(message):
    request_url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"
    response = requests.get(request_url)
    response_text = response.text
    today_json = json.loads(response_text)
    msg = ""
    hama={} 
    index = 1
    for sdict in today_json:
        if message in str(sdict["title"]):
            hama[index]={}
            hama[index]["title"]= sdict["title"]
            for s in sdict["showInfo"]:
                #msg+= (+"\n"+s["endTime"]+"\n"+s["location"]+"\n"+s["price"])+"\n"
                hama[index]["time"]=s["time"]
                hama[index]["endTime"]=s["endTime"]
                hama[index]["location"]=s["location"]
                index = index + 1
    #print (hama)
    for i in hama:
        msg+=str(i)+".\n名稱："+hama[i]["title"]+"\n開始時間："+hama[i]["time"]+"\n結束時間："+hama[i]["endTime"]+"\n地址："+hama[i]["location"]+"\n\n"
    return msg