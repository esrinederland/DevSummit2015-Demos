import requests
import json
from Password import PassWord, UserName

print "Start 12-Adding Features"
x = 1493510
y = 6894824

layerUrl = "http://services6.arcgis.com/4ARm2gylKRCZD9dM/arcgis/rest/services/windmills/FeatureServer/0"

print "Creating Feature"
features = []

feature ={}
feature["attributes"] = {}
feature["attributes"]["NAME"] = "Our berlin windmill"
feature["geometry"] = {}
feature["geometry"]["x"] = x
feature["geometry"]["y"] = y

features.append(feature)

print "Getting token"
#get Token
token_URL = 'https://www.arcgis.com/sharing/generateToken'
token_params = {'username':UserName,'password': PassWord,'referer': 'http://www.arcgis.com','f':'json','expiration':60}
r = requests.post(token_URL,token_params)
token_obj= r.json()
token = token_obj["token"]

print "sending request"
addFeatureUrl = "{}/AddFeatures".format(layerUrl,token)
params = {'token':token,'features':json.dumps(features),'f':'json'}
    
r = requests.post(addFeatureUrl,params)
print r.json()

print "Script complete"