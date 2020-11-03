# import os
# from flask import Flask, request, jsonify, render_template
# from firebase_admin import credentials, firestore, initialize_app
import json

from firebase_admin import credentials, firestore, initialize_app

from model import Spots

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
    spots = Spots()
    # spots.id=item.get("Id")
    spots.id=str(index)
    spots.name=item.get("Name")
    spots.description=item.get("Description")
    spots.detail=item.get("Toldescribe")
    spots.phone=item.get("Tel")
    spots.address=item.get("Add")
    spots.zipcode=item.get("Zipcode")
    spots.city=item.get("Region")
    spots.town=item.get("Town")
    spots.ticket=item.get("Ticketinfo")
    spots.remark=item.get("Remarks")

    # print(spots.name)
    result = spots_dataset.document(spots.id).set(spots.__dict__)
    print("add %d item success" % index)
    print("info :\n%s" % result)
    # break
