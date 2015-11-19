import requests
import json
from Password import PassWord, UserName

print "Start 13-Creating Groups"

print "Getting token"
#get Token
token_URL = 'https://www.arcgis.com/sharing/generateToken'
token_params = {'username':UserName,'password': PassWord,'referer': 'http://www.arcgis.com','f':'json','expiration':60}
r = requests.post(token_URL,token_params)
token_obj= r.json()
token = token_obj["token"]

print "Creating group parameters"
newGroupName = "Hello Berlin"
newGroupDesc = "Group to show how to create groups"
newGroupParams = {'title':newGroupName,'access':'account','description':newGroupDesc, "isViewOnly":True,"isInvitationOnly":True,"tags":"Windmills_Tag"}

url='http://www.arcgis.com/sharing/rest/community/createGroup?f=json&token={}'.format(token)

print "Sending request"
r = requests.post(url,newGroupParams)
print r.json()

print "Script complete"