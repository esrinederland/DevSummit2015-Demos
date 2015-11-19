import requests
import json
import logging, datetime
from Password import PassWord, UserName

def main():
    LogMessage("Start 11-Sharing With Groups")

    #get Token
    LogMessage("Create a ArcGIS Online Token")
    token_URL = 'https://www.arcgis.com/sharing/generateToken'
    token_params = {'username':UserName,'password': PassWord,'referer': 'http://www.arcgis.com','f':'json','expiration':60}
    r = requests.post(token_URL,token_params)
    token_obj= r.json()
    LogMessage(token_obj)
    token = token_obj["token"]


    #get featureserviceid
    LogMessage("Searching for featureservice itemid")
    serviceID = GetAGOLIDByNameAndType("windmills","Feature Service",token)
    LogMessage("Featureservice itemid: {}".format(serviceID))

    #get webmap id
    LogMessage("Searching for WebMap itemid")
    webMapID = GetAGOLIDByNameAndType("Windmill Map Berlin2015","Web Map",token)
    LogMessage("WebMap itemid: {}".format(webMapID))

    #get groupid
    wherestring='title:"Berlin Python 2015" AND owner:"'+UserName+'"'
    questionParams = {'q':wherestring,'f':'json','token':token}
    groupSearchUrl = "http://www.arcgis.com/sharing/rest/community/groups"
    r = requests.post(groupSearchUrl,questionParams)
    searchResults = r.json()
    LogMessage(searchResults)
    
    #!!!never do this, shame on you Maarten !!!
    groupid = searchResults["results"][0]["id"]

    #share featureservice
    shareurl = "http://www.arcgis.com/sharing/rest/content/users/{}/items/{}/share?f=json&token={}".format(UserName,serviceID,token)
    shareParams = {'everyone':False,'org':False,'groups':groupid}
    r = requests.post(shareurl,shareParams)
    LogMessage(r.json())

    #share webmap
    shareurl = "http://www.arcgis.com/sharing/rest/content/users/{}/items/{}/share?f=json&token={}".format(UserName,webMapID,token)
    shareParams = {'everyone':False,'org':False,'groups':groupid}
    r = requests.post(shareurl,shareParams)
    LogMessage(r.json())

    LogMessage("Script Complete")

def LogMessage(msg):
     GetLogger().info(msg)

_logger = None
def GetLogger():
    global _logger
    if _logger == None:
        fh = logging.FileHandler(r"D:\Berlin\Part 3 - ArcGIS Services\Logs\11-sharewithgroups_{}.log".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
        fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y%m%d-%H:%M:%S'))
        ch = logging.StreamHandler()
        ch.setFormatter(fh.formatter)

        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(fh)
        logging.getLogger().addHandler(ch)

        _logger = logging.getLogger()
    return _logger

def GetAGOLIDByNameAndType(name,typeName,token):

    wherestring='title:"{}" AND type:"{}"'.format(name,typeName)
    questionParams = {'q':wherestring}

    url = r"http://www.arcgis.com/sharing/rest/search?f=json&token={}".format(token)

    r = requests.post(url,questionParams)
    retObject = r.json()
    returnID = None
    if retObject["total"] > 0:

        returnID = retObject["results"][0]["id"]
        LogMessage(typeName+" exists, id:"+returnID)
    else:
        LogMessage(typeName+" does not exist")
    return returnID

if __name__=="__main__":
    main()