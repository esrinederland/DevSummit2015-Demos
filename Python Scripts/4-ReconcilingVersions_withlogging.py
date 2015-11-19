import arcpy, logging, datetime


def LogMessage(msg):
    logging.getLogger().info(msg)

fh = logging.FileHandler(r"D:\Berlin\Part 1 - Administration\Logs\4-reconcilelog_{}.log".format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y%m%d-%H:%M:%S'))
ch = logging.StreamHandler()
ch.setFormatter(fh.formatter)

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(fh)
logging.getLogger().addHandler(ch)

LogMessage("Start 4-Reconciling Versions with logging")

# Set an gdb admin connection variable.
adminConn = r"D:\Berlin\Part 1 - Administration\DEVSUMMIT_SDE.sde"
LogMessage("Connecting to the geodatabase as the gdb admin user (sde)")

# Set a few environment variables
arcpy.env.workspace = adminConn
arcpy.env.overwriteOutput = True

# For demo purposes we will block connections to the geodatabase during schema rec/post/compress.
LogMessage("The database is no longer accepting connections")
arcpy.AcceptConnections(adminConn, False)

# Disconnect any connected users.
LogMessage("Disconnecting all users")
arcpy.DisconnectUser(adminConn, 'ALL')

# Get a list of versions to pass into the ReconcileVersions tool.
# Only reconcile versions that are children of Default
LogMessage("Compiling a list of versions to reconcile")
verList = arcpy.da.ListVersions(adminConn)
versionList = [ver.name for ver in verList if ver.parentVersionName == 'sde.DEFAULT']

# Execute the ReconcileVersions tool.
try:
    LogMessage("Reconciling versions")
    arcpy.ReconcileVersions_management(adminConn, "ALL_VERSIONS", "sde.DEFAULT",
                                       versionList,"LOCK_ACQUIRED", "NO_ABORT",
                                       "BY_OBJECT", "FAVOR_TARGET_VERSION","POST",
                                       "KEEP_VERSION", sys.path[0] + "/reclog.txt")
    LogMessage('Reconcile and post executed successfully.')
    LogMessage('Reconcile Log is below.') #warning this can be very long.
    LogMessage(open(sys.path[0] + "/reclog.txt", 'r').read())
except:
    LogMessage('Reconcile & post failed. Error message below.' + arcpy.GetMessages())

# Run the compress tool.
try:
    LogMessage("Running compress")
    arcpy.Compress_management(adminConn)
    #if the compress is successful add a message.
    LogMessage('Compress was successful.')
except:
    #If the compress failed, add a message.
    LogMessage('\nCompress failed: error message below.' + arcpy.GetMessages())


#Update statistics and idexes for the system tables
# Note: to use the "SYSTEM" option the user must be an geodatabase or database administrator.
try:
    LogMessage("Rebuilding indexes on the system tables")
    arcpy.RebuildIndexes_management(adminConn, "SYSTEM")
    LogMessage('Rebuilding of system table indexes successful.')
except:
    LogMessage('Rebuild indexes on system tables fail: error message below.\n\r' + arcpy.GetMessages())

try:
    LogMessage("Updating statistics on the system tables")
    arcpy.AnalyzeDatasets_management(adminConn, "SYSTEM")
    LogMessage('Analyzing of system tables successful.')
except:
    LogMessage('Analyze system tables failed: error message below.\n\r' + arcpy.GetMessages())

# Allow connections again.
LogMessage("Allow users to connect to the database again")
arcpy.AcceptConnections(adminConn, True)
LogMessage("Finshed gdb admin user (sde) tasks \n")