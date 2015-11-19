import arcpy

print "Start 6-Create Featureclass"

connection = "D:\Berlin\Part 2 - DatabaseContents\DEVSUMMIT.sde"
out_name = "SoundRadius"
geometry_type = "POLYGON"
template = None
has_m = "DISABLED"
has_z = "DISABLED"

fullPath = connection + "\\" + out_name

# Use Describe to get a SpatialReference object
spatial_reference = arcpy.SpatialReference(4326) #4326: WGS84

if arcpy.Exists(fullPath):
    print "FeatureClass already exists"
    arcpy.Delete_management(fullPath)

print "Creating featureclass"
arcpy.CreateFeatureclass_management(connection, out_name, geometry_type, template, has_m, has_z, spatial_reference)

print "Adding fields"
arcpy.AddField_management(fullPath,"NAME","TEXT","","",255,"Name","NON_NULLABLE","REQUIRED")
arcpy.AddField_management(fullPath,"RADIUS","SHORT","","","","Radius","NON_NULLABLE","REQUIRED")

print "script complete"