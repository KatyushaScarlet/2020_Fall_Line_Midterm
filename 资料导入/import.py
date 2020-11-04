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

index = 0
for item in node:
    index += 1
    spot = SpotModel()
    # spot.id=item.get("Id")
    spot.id=str(index)
    spot.name=item.get("Name")
    spot.description=item.get("Description")
    spot.detail=item.get("Toldescribe")
    spot.phone=item.get("Tel")
    spot.address=item.get("Add")
    spot.zipcode=item.get("Zipcode")
    spot.city=item.get("Region")
    spot.town=item.get("Town")
    spot.ticket=item.get("Ticketinfo")
    spot.remark=item.get("Remarks")
    spot.time=item.get("Opentime")

    # print(spot.name)
    result = spots_dataset.document(spot.id).set(spot.__dict__)
    print("add %d item success" % index)
    print("info :\n%s" % result)
    # break
