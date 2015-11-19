import arcpy
import requests
import logging
import datetime
import time
import os
from Password import UserName, PassWord
import xml.dom.minidom as DOM

mxdPath = r"D:\Berlin\Part 3 - ArcGIS Services\Windmills.mxd"
sdDraftFile =  r"D:\Berlin\Part 3 - ArcGIS Services\Windmills.sddraft"
sdFile = r"D:\Berlin\Part 3 - ArcGIS Services\Windmills.sd"
serviceName = "windmills"
serviceSummary = "Windmills Summary"
serviceTags = "Windmills_Tag"

def main():
    LogMessage("Start 09-Publish MXD")

    #1. opening MXD
    LogMessage("opening mxd")
    mxd = arcpy.mapping.MapDocument(mxdPath)

    #2. Creating SD Draft
    LogMessage("Creating SD Draft")
    arcpy.mapping.CreateMapSDDraft(mxd, sdDraftFile, serviceName, 'MY_HOSTED_SERVICES', summary=serviceSummary, tags=serviceTags)

    #3. Edit SD draft
    LogMessage("Edit SD Draft")
    EditSDDraft(sdDraftFile)

    #4. Analyze SD Draft
    LogMessage("Analize SDDraft")
    analysis = arcpy.mapping.AnalyzeForSD(sdDraftFile)

    #5. stage SDDraft
    LogMessage("Staging service")
    if os.path.exists(sdFile):
        os.remove(sdFile)
    arcpy.StageService_server(sdDraftFile, sdFile)

    #6. Getting a arcgis online token
    LogMessage("Create a ArcGIS Online Token")
    token_URL = 'https://www.arcgis.com/sharing/generateToken'
    token_params = {'username':UserName,'password': PassWord,'referer': 'http://www.arcgis.com','f':'json','expiration':60}
    r = requests.post(token_URL,token_params)
    token_obj= r.json()
    LogMessage(token_obj)
    token = token_obj["token"]

    #7. Start uploading
    LogMessage("Upload Service Definition")
    currentID = GetAGOLIDByNameAndType(serviceName, "Service Definition",token)
    uploadURL = "http://www.arcgis.com/sharing/rest/content/users/{}/addItem".format(UserName)
    if(currentID != None):
        uploadURL = 'http://www.arcgis.com/sharing/rest/content/users/{}/items/{}/update'.format(UserName, currentID)
    url = uploadURL + "?f=json&token=" + token + "&filename=" + sdFile + "&type=Service Definition" + "&title="+serviceName + "&tags="+serviceTags + "&description=" + serviceSummary
    filesUp = {"file": open(sdFile, 'rb')}
    r = requests.post(url, files=filesUp);
    
    resultJson = r.json()
    LogMessage(resultJson)
    itemID = resultJson['id']

    #8. Start publishing
    LogMessage("Start publish job")
    publishURL = 'http://www.arcgis.com/sharing/rest/content/users/{}/publish'.format(UserName)
    url = publishURL + "?f=json&token=" + token 
    pubParams ='{"name":"'+serviceName+ '"}'
    publishParams = {'itemID': itemID, 'filetype': 'serviceDefinition','overwrite':True,  'publishParameters':pubParams}
    r = requests.post(url,publishParams)
    
    resultJson = r.json()
    LogMessage(resultJson)
    jobid = resultJson["services"][0]["jobId"]
    serviceItemId = resultJson["services"][0]["serviceItemId"]

    #9. Checking publish status
    LogMessage("Check publish job status")
    jobstatus = "processing"
    while jobstatus=="processing":
        
        url = "http://www.arcgis.com/sharing/rest/content/users/{}/items/{}/status?f=json&token={}".format(UserName,serviceItemId,token)
        query_dict = {'jobid': jobid, 'jobtype': 'publish'}
        r = requests.post(url,query_dict)
        resultJson = r.json()
        LogMessage(resultJson)
        jobstatus = resultJson["status"]
        LogMessage("Status for service {} - job {} is {}".format(serviceName,jobid,jobstatus))
        if jobstatus=="processing":
            time.sleep(5)

    #10. Celebrate
    LogMessage("Publish complete")

def EditSDDraft(sdDraftFile):
    doc = DOM.parse(sdDraftFile)
    # Change service from map service to feature service
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        # Get the TypeName we want to disable.
        if typeName.firstChild.data == "MapServer":
            typeName.firstChild.data = "FeatureServer"

    #Turn off caching
    configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "isCached":
                    # turn on caching
                    keyValue.nextSibling.firstChild.data = "false"

    #Turn on feature access capabilities
    configProps = doc.getElementsByTagName('Info')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "WebCapabilities":
                    # turn on caching
                    keyValue.nextSibling.firstChild.data = "Query" #,Create,Update,Delete,Uploads,Editing"

    f = open(sdDraftFile, 'w')
    doc.writexml( f )
    f.close()

def LogMessage(msg):
     GetLogger().info(msg)

_logger = None
def GetLogger():
    global _logger
    if _logger == None:
        fh = logging.FileHandler(r"D:\Berlin\Part 3 - ArcGIS Services\Logs\09-publishmxd_{}.log".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
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