#-------------------------------------------------------------------------------
# Name:        2-CreateDatabase
# Purpose:
#
# Author:      hulzen
#
# Created:     12-11-2015
# Copyright:   (c) esri 2015
#-------------------------------------------------------------------------------
import arcpy
import os

print "Start 2-CreateDatabase"
databasename = "DEVSUMMIT"
connectionFolderPath = r"D:\Berlin\Part 1 - Administration"
connectionFilepath = os.path.join(connectionFolderPath,databasename+".sde")
roleName = "editor"
dbInstance = "ESRIBX0373\SQLEXPRESS"

print "Creating database"
#create database
arcpy.CreateEnterpriseGeodatabase_management("SQL_Server", dbInstance, databasename, "OPERATING_SYSTEM_AUTH",
                                             "", "", "SDE_SCHEMA",
                                             "sde", "sde","",r"D:\Berlin\Part 1 - Administration\keycodes")

# Create Connection
print "Creating connection"
arcpy.CreateDatabaseConnection_management(connectionFolderPath,databasename,"SQL_SERVER",
                                          dbInstance,"OPERATING_SYSTEM_AUTH","","","SAVE_USERNAME",databasename)

# Create an editor role
print "Creating role"
arcpy.CreateRole_management(connectionFilepath, roleName)

# Create list of users
print "Creating users"
userList = ['jack', 'linda', 'bill']

# Create users and assign to editor role
for user in userList:
    arcpy.CreateDatabaseUser_management(connectionFilepath, "DATABASE_USER", user, "SomePassword01", roleName)

#import xml workspace document
print "Importing XML Workspace"
arcpy.ImportXMLWorkspaceDocument_management(connectionFilepath,
                                                'D:\Berlin\Part 1 - Administration\WINDMILLS.XML',
                                                'DATA')

print "Script complete"