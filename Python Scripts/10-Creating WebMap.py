import requests
import json
import logging, datetime
from Password import PassWord, UserName

def main():
    LogMessage("Start 10-Creating WebMap")

    #get Token
    LogMessage("Create a ArcGIS Online Token")
    token_URL = 'https://www.arcgis.com/sharing/generateToken'
    token_params = {'username':UserName,'password': PassWord,'referer': 'http://www.arcgis.com','f':'json','expiration':60}
    r = requests.post(token_URL,token_params)
    token_obj= r.json()
    LogMessage(token_obj)
    token = token_obj["token"]

    #search service
    LogMessage("Searching for featureservice itemid")
    serviceID = GetAGOLIDByNameAndType("windmills","Feature Service",token)
    LogMessage("Featureservice itemid: {}".format(serviceID))

    #get service url
    LogMessage("Searching for featureservice url")
    serviceItemUrl = "http://www.arcgis.com/sharing/rest/content/items/{}?f=json&token={}".format(serviceID,token)
    r = requests.get(serviceItemUrl)
    serviceJson= r.json()
    serviceURL = serviceJson["url"]
    LogMessage(serviceURL)
    LogMessage("featureservice url: {}".format(serviceURL))

    #open webmap data
    LogMessage("opening webmap template data file")
    f = open(r"D:\Berlin\Part 3 - ArcGIS Services\webmapdata.json","r")
    webmapData = f.read()

    #replace id's and services
    LogMessage("Replacing items in webmapdata")
    webmapData = webmapData.replace("@serviceID@",serviceID)
    webmapData = webmapData.replace("@serviceURL@",serviceURL)

    #create webmap info
    LogMessage("Creating webmap info object")
    webmapInfo = {}
    webmapInfo["title"] = "Windmill Map Berlin2015"
    webmapInfo["tags"] = "Windmills_Tag"
    webmapInfo["description"] = "Hello Berlin, this is newly created webmap"
    webmapInfo["type"] = "Web Map"
    webmapInfo["text"] = webmapData

    #upload webmap
    LogMessage("Add item to ArcGIS Online")
    addItemUrl = "http://www.arcgis.com/sharing/rest/content/users/{}/addItem?f=json&token={}".format(UserName,token)
    r = requests.post(addItemUrl,webmapInfo)
    LogMessage(r.json())
    LogMessage("Script complete")
    
def LogMessage(msg):
     GetLogger().info(msg)

_logger = None
def GetLogger():
    global _logger
    if _logger == None:
        fh = logging.FileHandler(r"D:\Berlin\Part 3 - ArcGIS Services\Logs\10-createwebmap_{}.log".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
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