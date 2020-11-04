# import os
# from flask import Flask, request, jsonify, render_template
# from firebase_admin import credentials, firestore, initialize_app
import json

from firebase_admin import credentials, firestore, initialize_app

from model import SpotModel

cred = credentials.Certificate('firebase-key.json')
initialize_app(cred)
db = firestore.client()
spots_dataset = db.collection('spots')



file = open("data.json",encoding="utf-8")
data = json.load(file)
node = data.get("XML_Head")
node = node.get("Infos")
node = node.get("Info")

# solve null and None problem
def transform(input):
    output = str(input)
    if(output == "None"):
        output = ""
    elif(output == "null"):
        output = ""

    return output


index = 0
for item in node:
    index += 1
    spot = SpotModel()
    # spot.id=transform(item.get("Id"))
    spot.id=str(index)
    spot.name=transform(item.get("Name"))
    spot.description=transform(item.get("Description"))
    spot.detail=transform(item.get("Toldescribe"))
    spot.phone=transform(item.get("Tel"))
    spot.address=transform(item.get("Add"))
    spot.zipcode=transform(item.get("Zipcode"))
    spot.city=transform(item.get("Region"))
    spot.town=transform(item.get("Town"))
    spot.ticket=transform(item.get("Ticketinfo"))
    spot.remark=transform(item.get("Remarks"))
    spot.time=transform(item.get("Opentime"))

    # print(spot.name)
    result = spots_dataset.document(spot.id).set(spot.__dict__)
    print("add %d item success" % index)
    print("info :\n%s" % result)
    # break


