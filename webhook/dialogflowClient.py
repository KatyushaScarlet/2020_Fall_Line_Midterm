import os
import json
import requests
import dialogflow_v2 as dialogflow
from dialogflowClientConfig import project_id
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToJson


os.environ ["GOOGLE_APPLICATION_CREDENTIALS"] = "serviceAccountKey.json"
language_code = 'zh-HK'


session_client = dialogflow.SessionsClient()


def getDialogflowJsonResponse(session, query_input):
    dialogflowResponse = session_client.detect_intent(session=session, query_input=query_input)
    jsonObj = MessageToJson(dialogflowResponse.query_result)
    response = json.loads(jsonObj)
    return response


def getfulfillmentMessages(dialogflowModel, response):
    if ('fulfillmentText' in response):
        fulfillmentMessages = response['fulfillmentMessages']
        #print(response['intent']['displayName'])
        print(response['fulfillmentMessages'])
        for fulfillmentMessage in fulfillmentMessages:
            dialogflowModel.responses.append(fulfillmentMessage['text']['text'][0])


def getResponsesByEvent(dialogflowModel):
    dialogflowParameters = Struct()
    dialogflowParameters['lineId'] = dialogflowModel.lineId

    if (dialogflowModel.eventName == 'retrieve_responseEvent'):
        dialogflowParameters['userName'] = dialogflowModel.parameters['name']
        dialogflowParameters['userPhone'] = dialogflowModel.parameters['phone']
        dialogflowParameters['userEmail'] = dialogflowModel.parameters['email']
        dialogflowParameters['userLineId'] = dialogflowModel.parameters['lineId']
        
    elif (dialogflowModel.eventName == 'update_responseEvent'):
        dialogflowParameters['originalName'] = dialogflowModel.parameters['name']
        dialogflowParameters['originalEmail'] = dialogflowModel.parameters['email']
    
    session = session_client.session_path(project_id, dialogflowModel.lineId)
    event_input = dialogflow.types.EventInput(name=dialogflowModel.eventName, parameters=dialogflowParameters, language_code=language_code)
    query_input = dialogflow.types.QueryInput(event=event_input)
    response = getDialogflowJsonResponse(session, query_input)
    print(response['intent']['displayName'])
    getfulfillmentMessages(dialogflowModel, response)


def eventDispatch(dialogflowModel):
    session = session_client.session_path(project_id, dialogflowModel.lineId)
    getResponsesByEvent(dialogflowModel)
    if (dialogflowModel.eventName == 'welcomeEvent'):
        dialogflowModel.eventName = 'menuEvent'
        getResponsesByEvent(dialogflowModel)
   
   
def queryDispatch(dialogflowModel):
    session = session_client.session_path(project_id, dialogflowModel.lineId)
    text_input = dialogflow.types.TextInput(text=dialogflowModel.queryInput, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = getDialogflowJsonResponse(session, query_input)
    print(response['intent']['displayName'])
    getfulfillmentMessages(dialogflowModel, response)
    
    if (set(['action','allRequiredParamsPresent']).issubset(response)):
        dialogflowModel.actionName = response['action']
        dialogflowModel.parameters = response['parameters']
        
        if (dialogflowModel.actionName == 'update'):
            for userData in response['outputContexts']:
                if ('phone' in userData['parameters']):
                    dialogflowModel.parameters['phone'] = userData['parameters']['phone']
            
        
    elif (set(['item']).issubset(response['parameters'])):
        dialogflowModel.eventName = 'update_' + response['parameters']['item'] + 'Event'
        eventDispatch(dialogflowModel)
        
    elif (set(['isFallback']).issubset(response['intent'])):
        dialogflowModel.eventName = 'menuEvent'
        eventDispatch(dialogflowModel)