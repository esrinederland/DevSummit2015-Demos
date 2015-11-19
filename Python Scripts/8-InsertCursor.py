import arcpy

print "Start 8-InsertCursor"

#featureclasses to use
fcin = "D:\Berlin\Part 2 - DatabaseContents\WindmillsRD.gdb\Windmills"
fcout ="D:\Berlin\Part 2 - DatabaseContents\WindmillsRD.gdb\SoundRadius"

#setting up cursors
searchCursor = arcpy.da.SearchCursor(fcin,  ['NAME', 'HEIGHT','SOUNDRADIUS', 'SHAPE@'])
insertCursor = arcpy.da.InsertCursor(fcout,['NAME', 'RADIUS','SHAPE@'])

for row in searchCursor:

    print(str(row[0]) + " " + str(row[1]))
    geom = row[3]
    
    newGeom = geom.buffer(row[2])
    
    insertCursor.insertRow((row[0],row[2],newGeom))
    print "Row for windmill with name {} created".format(row[0])

del searchCursor
del insertCursor

print "done"