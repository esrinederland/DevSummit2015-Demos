import arcpy

print "Start 7-SearchCursor"

#setting up the featureclass path
fc = "D:\Berlin\Part 2 - DatabaseContents\DEVSUMMIT.sde\Windmills"

#creating the cursor 
cursor = arcpy.SearchCursor(fc,where_clause="HEIGHT >=200")

#loop through the cursor
row = cursor.next()
while row:
    print(str(row.getValue("NAME")) + " " + str(row.getValue("HEIGHT")))

    row = cursor.next()

print "script complete"