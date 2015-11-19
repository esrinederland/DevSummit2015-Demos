import arcpy

print("Start 3-Reconciling Versions")

# Set an gdb admin connection variable.
adminConn = r"D:\Berlin\Part 1 - Administration\DEVSUMMIT_SDE.sde"
print("Connecting to the geodatabase as the gdb admin user (sde)")

# Set a few environment variables
arcpy.env.workspace = adminConn
arcpy.env.overwriteOutput = True

# For demo purposes we will block connections to the geodatabase during schema rec/post/compress.
print("The database is no longer accepting connections")
arcpy.AcceptConnections(adminConn, False)

# Disconnect any connected users.
print("Disconnecting all users")
arcpy.DisconnectUser(adminConn, 'ALL')

# Get a list of versions to pass into the ReconcileVersions tool.
# Only reconcile versions that are children of Default
print("Compiling a list of versions to reconcile")
verList = arcpy.da.ListVersions(adminConn)
versionList = [ver.name for ver in verList if ver.parentVersionName == 'sde.DEFAULT']

# Execute the ReconcileVersions tool.
try:
    print("Reconciling versions")
    arcpy.ReconcileVersions_management(adminConn, "ALL_VERSIONS", "sde.DEFAULT",
                                       versionList,"LOCK_ACQUIRED", "NO_ABORT",
                                       "BY_OBJECT", "FAVOR_TARGET_VERSION","POST",
                                       "KEEP_VERSION", sys.path[0] + "/reclog.txt")
    print('Reconcile and post executed successfully.')
    print('Reconcile Log is below.') #warning this can be very long.
    print(open(sys.path[0] + "/reclog.txt", 'r').read())
except:
    print('Reconcile & post failed. Error message below.' + arcpy.GetMessages())

# Run the compress tool.
try:
    print("Running compress")
    arcpy.Compress_management(adminConn)
    #if the compress is successful add a message.
    print('Compress was successful.')
except:
    #If the compress failed, add a message.
    print('\nCompress failed: error message below.' + arcpy.GetMessages())


#Update statistics and idexes for the system tables
# Note: to use the "SYSTEM" option the user must be an geodatabase or database administrator.
try:
    print("Rebuilding indexes on the system tables")
    arcpy.RebuildIndexes_management(adminConn, "SYSTEM")
    print('Rebuilding of system table indexes successful.')
except:
    print('Rebuild indexes on system tables fail: error message below.\n\r' + arcpy.GetMessages())

try:
    print("Updating statistics on the system tables")
    arcpy.AnalyzeDatasets_management(adminConn, "SYSTEM")
    print('Analyzing of system tables successful.')
except:
    print('Analyze system tables failed: error message below.\n\r' + arcpy.GetMessages())

# Allow connections again.
print("Allow users to connect to the database again")
arcpy.AcceptConnections(adminConn, True)
print("Finshed gdb admin user (sde) tasks \n")