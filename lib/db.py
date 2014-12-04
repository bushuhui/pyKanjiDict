#!/usr/bin/env python


"""
	web dict db connect module
	
	Note:
		1. For start or stop MySQL server, please set MYSQL_ROOT enviroment
			variable to MySQL server root directory.
"""


import MySQLdb, os, sys


def GetDBSetting():
	# set default value
	dbSetting = {}
	
	dbSetting["host"] = "127.0.0.1"
	dbSetting["port"] = 3306
	dbSetting["user"] = "root"
	dbSetting["passwd"] = ""
	dbSetting["db"] = "japdict2"

	try:
		if( os.path.isfile("dbsetting.cfg") ):
			for l in file("dbsetting.cfg").readlines():
				l2 = l.split("=")
				
				if( l2[0].strip() == "" or len(l2) < 2):
					return dbSetting
				
				sName = l2[0].strip()
				sVal = l2[1].strip()
				
				if sName == "port":
					dbSetting[sName] = int(sVal)
				else:
					dbSetting[sName] = sVal
	except:
		return -1
	
	return dbSetting

#
# Connnect to given data base
#
def ConnDB(dbSettings = None, dbname = ""):
	ds = dbSettings
	
	if( dbSettings == None ):
		try:
			ds = GetDBSetting()
			if( type(ds).__name__ == "int" ):
				return -2
		except:
			return -1
	
	database = dbname
	if( dbname == "" ):
		database = ds["db"]
		
	# Create a connection object, then use it to create a cursor
	Con = MySQLdb.connect(host=ds["host"], port=ds["port"], 
		user=ds["user"], passwd=ds["passwd"], db=database)
	Cursor = Con.cursor()

	return (Con, Cursor)


#
# Close database connection
#
def CloseDB(con):
	try:
		con.close()
	except:
		print "ERR: Failed to close data base connect"
		
	return
		
# fixme:
# where use didn't have administrator privilage
# call 'tasklist" will be failed
def GetServerPID():
	if( sys.platform != "win32" ):
		return -2
	
	stdout = os.popen("tasklist")
	for l in stdout.readlines():
		ll = l.split(" ")
		if( ll[0] == "mysqld.exe" ):
			for ite in ll[1:]:
				if( ite.isdigit() ):
					return int(ite)
	
	return -1

def StartDBServer():
	if( sys.platform != "win32" ):
		return -2
	
	srvPid = GetServerPID()
	if( srvPid != -1 ):
		return 0
	
	try:
		if( os.environ.has_key("MYSQL_ROOT") ):
			p = os.environ["MYSQL_ROOT"]
			s = os.path.join(p, "bin", "mysqld.exe")
		else:
			s = os.path.join(os.getcwd(), "..", "progs", "mysql", "bin", "mysqld.exe")
			#print s
			
		r = os.spawnl(os.P_NOWAIT, s)
		return r
	except:
		return -1
	
def StopDBServer_v1():
	if( sys.platform != "win32" ):
		return -2
	
	iSrvPid = GetServerPID()
	if( iSrvPid < 0 ):
		return -1
	else:
		exeStr = "taskkill /PID %d /F" % iSrvPid
		os.system(exeStr)
	
	return 0

def StopDBServer():
	if( sys.platform != "win32" ):
		return -2
	
	srvPid = GetServerPID()
	if( srvPid < 0 ):
		return -3
	
	try:
		if( os.environ.has_key("MYSQL_ROOT") ):
			p = os.environ["MYSQL_ROOT"]
			s = os.path.join(p, "bin", "mysqladmin.exe shutdown")
		else:
			s = os.path.join(os.getcwd(), "..", "progs", "mysql", "bin", "mysqladmin.exe shutdown")			
	
		#r = os.spawnl(os.P_NOWAIT, "mysql\\bin\\mysqladmin.exe shutdown")
		#s = os.path.join(os.getcwd(), "mysql", "bin", "mysqladmin.exe shutdown")
		os.system(s)
		return 0
	except:
		return -1

def test():
	#StartDBServer()
	#print "mysqld pid=", GetServerPID()
	#StopDBServer()
	con = ConnDB()
	if( type(con).__name__ == "int" ):
		print con
	else:
		print "connect success"
	
	
if( __name__ == "__main__" ):
	test()
	